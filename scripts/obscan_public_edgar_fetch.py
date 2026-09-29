"""Owner-invoked, public SEC metadata fetcher. No market quotes, tokens or scheduler.

Default is DRY RUN. Requires --enable-network AND a genuine identifying User-Agent.
One request per second, <=20 reviewed issuer CIKs, bounded response sizes, no web crawl.
Usage:
  python scripts/obscan_public_edgar_fetch.py --output ./local-obscan --ciks 0000320193
  python scripts/obscan_public_edgar_fetch.py --enable-network \
    --user-agent 'Your Research Name contact@yourdomain.com' --output ./local-obscan \
    --ciks 0000320193
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

MAX_BYTES = 10_000_000
ALLOWED_HOSTS = frozenset(("www.sec.gov", "data.sec.gov"))
CIK_RE = re.compile(r"^\d{1,10}$")


def targets(ciks: list[str]) -> list[tuple[str, str]]:
    if len(ciks) > 20:
        raise ValueError("maximum twenty SEC issuer requests per explicit run")
    answer = [("company_tickers_exchange.json",
               "https://www.sec.gov/files/company_tickers_exchange.json")]
    seen: set[str] = set()
    for value in ciks:
        if not CIK_RE.fullmatch(value):
            raise ValueError("issuer CIK must be 1-10 digits, not a ticker or URL")
        cik=value.zfill(10)
        if cik not in seen:
            seen.add(cik)
            answer.append((f"CIK{cik}.json", f"https://data.sec.gov/submissions/CIK{cik}.json"))
    return answer


def _header_path(directory: Path, filename: str) -> Path:
    return directory / f"{filename}.http-metadata.json"


def _read_headers(directory: Path, filename: str) -> dict[str, str]:
    try:
        payload=json.loads(_header_path(directory,filename).read_text(encoding="utf-8"))
        return {k:payload[k] for k in ("etag", "last_modified") if isinstance(payload.get(k),str)}
    except (OSError, ValueError, TypeError):
        return {}


def fetch_public_sec(*, ciks: list[str], output: Path, user_agent: str,
                     enable_network: bool = False, delay_seconds: float = 1.0,
                     opener=urlopen, sleeper=time.sleep) -> dict[str, object]:
    planned=targets(ciks)
    if not enable_network:
        return {"state":"DRY_RUN_NO_REQUESTS","planned_urls":[url for _,url in planned],
                "price_feed":False,"automatic_scheduler":False}
    if not isinstance(user_agent,str) or "@" not in user_agent or " " not in user_agent or len(user_agent)>180:
        raise ValueError("provide the real research entity and contact address in User-Agent")
    if delay_seconds < 1.0:
        raise ValueError("public SEC pacing may not be raised above one request per second")
    if not isinstance(output,Path):
        raise TypeError("output directory must be a Path")
    output.mkdir(parents=True,exist_ok=True)
    if output.resolve() == Path.cwd().resolve():
        raise ValueError("use a dedicated local output directory")
    results=[]
    for index,(filename,url) in enumerate(planned):
        parts=urlsplit(url)
        if parts.scheme!="https" or parts.hostname not in ALLOWED_HOSTS:
            raise ValueError("refusing unapproved URL")
        if index:sleeper(delay_seconds)
        previous=_read_headers(output,filename)
        headers={"User-Agent":user_agent,"Accept":"application/json"}
        if previous.get("etag"):headers["If-None-Match"]=previous["etag"]
        if previous.get("last_modified"):headers["If-Modified-Since"]=previous["last_modified"]
        req=Request(url,headers=headers,method="GET")
        try:
            with opener(req, timeout=15) as response:
                final=urlsplit(response.geturl())
                if final.scheme!="https" or final.hostname not in ALLOWED_HOSTS:
                    raise ValueError("SEC endpoint redirected to unapproved host")
                raw=response.read(MAX_BYTES+1)
                if len(raw)>MAX_BYTES:
                    raise ValueError("SEC public response exceeds explicit size budget")
                payload=json.loads(raw)
                if not isinstance(payload,dict):
                    raise ValueError("SEC public response was not JSON object")
                tmp=output/f"{filename}.partial"
                tmp.write_text(json.dumps(payload,sort_keys=True),encoding="utf-8")
                tmp.replace(output/filename)
                metadata={"etag":response.headers.get("ETag",""),
                          "last_modified":response.headers.get("Last-Modified",""),
                          "retrieved_at":datetime.now(timezone.utc).isoformat(),
                          "url":url}
                _header_path(output,filename).write_text(json.dumps(metadata,indent=2),encoding="utf-8")
                results.append({"file":filename,"state":"UPDATED","size_bytes":len(raw)})
        except HTTPError as exc:
            if exc.code==304 and (output/filename).exists():
                results.append({"file":filename,"state":"NOT_MODIFIED"})
            elif exc.code==429:
                results.append({"file":filename,"state":"RATE_LIMIT_HOLD_STOP","retry_after":exc.headers.get("Retry-After")})
                break  # No retries, proxies, parallel connections or rate-limit evasion.
            else:
                results.append({"file":filename,"state":f"HTTP_HOLD_{exc.code}"})
                break
        except (URLError, ValueError, json.JSONDecodeError, TimeoutError) as exc:
            results.append({"file":filename,"state":"SOURCE_HOLD","reason":str(exc)[:180]})
            break
    return {"state":"PUBLIC_METADATA_ONLY","requests_attempted":len(results),"files":results,
            "source":"SEC EDGAR","price_feed":False,"real_time_market_data":False,
            "execution_ready":False,"automatic_scheduler":False}


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",required=True,type=Path)
    parser.add_argument("--ciks",nargs="*",default=[])
    parser.add_argument("--user-agent",default="")
    parser.add_argument("--enable-network",action="store_true")
    args=parser.parse_args()
    print(json.dumps(fetch_public_sec(ciks=args.ciks,output=args.output,
                                     user_agent=args.user_agent,enable_network=args.enable_network),indent=2))


if __name__=="__main__":
    main()
