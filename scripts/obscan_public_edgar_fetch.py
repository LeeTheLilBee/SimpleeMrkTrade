"""Owner-invoked, official SEC EDGAR submissions + companyfacts collector.

Default DRY RUN, zero HTTP. Network activation requires --enable-network AND
a real organization/contact User-Agent. No API key, browser fetch, cron,
proxy/crawl, order execution, price feed, guessed ticker, or paid infrastructure.

Example:
 python scripts/obscan_public_edgar_fetch.py --output ./local-obscan --ciks 0000320193
 python scripts/obscan_public_edgar_fetch.py --enable-network \
   --user-agent "Your Organization research-contact@your-domain.com" \
   --output ./local-obscan --ciks 0000320193
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, HTTPRedirectHandler, build_opener

MAX_BYTES = 32_000_000
ALLOWED_HOSTS = frozenset(("www.sec.gov","data.sec.gov"))
CIK_RE = re.compile(r"^\d{1,10}$")
CONTACT_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
ROOT_CROSSREF = ("company_tickers_exchange.json",
                 "https://www.sec.gov/files/company_tickers_exchange.json")


class NoRedirect(HTTPRedirectHandler):
    """Do not follow redirects to an unknown host before verifying its URL."""
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        raise ValueError("SEC endpoint redirect requires a separate source review")


def _default_opener(req,timeout=15):
    return build_opener(NoRedirect()).open(req,timeout=timeout)


def targets(ciks:list[str])->list[tuple[str,str]]:
    if len(ciks)>20:
        raise ValueError("maximum twenty expressly selected issuer CIKs per run")
    answer=[ROOT_CROSSREF]
    seen=set()
    for value in ciks:
        if not isinstance(value,str) or not CIK_RE.fullmatch(value):
            raise ValueError("issuer CIK must be 1–10 digits, not a ticker or URL")
        cik=value.zfill(10)
        if cik in seen:continue
        seen.add(cik)
        answer.extend((
            (f"CIK{cik}.json",f"https://data.sec.gov/submissions/CIK{cik}.json"),
            (f"CIK{cik}.companyfacts.json",
             f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"),
        ))
    return answer


def _head_path(root:Path,name:str)->Path:
    return root/f"{name}.http-metadata.json"


def _read_headers(root:Path,name:str)->dict[str,str]:
    try:
        payload=json.loads(_head_path(root,name).read_text(encoding="utf-8"))
        return {k:payload[k] for k in ("etag","last_modified") if isinstance(payload.get(k),str)}
    except (OSError,ValueError,TypeError):return {}


def _validate_payload(name:str,payload:object)->None:
    if not isinstance(payload,dict):raise ValueError("SEC response was not a JSON object")
    if name=="company_tickers_exchange.json":
        if not isinstance(payload.get("fields"),list) or not isinstance(payload.get("data"),list):
            raise ValueError("official cross-reference columns missing")
    else:
        expected=name[3:13]
        cik=payload.get("cik")
        if isinstance(cik,bool) or str(cik).zfill(10)!=expected:
            raise ValueError("SEC issuer response CIK mismatch")
        if name.endswith(".companyfacts.json"):
            if not isinstance(payload.get("facts"),dict):
                raise ValueError("SEC financial-facts payload malformed")
        elif not isinstance(payload.get("filings"),dict) or not isinstance(payload["filings"].get("recent"),dict):
            raise ValueError("SEC submissions response missing filing history")


def fetch_public_sec(*,ciks:list[str],output:Path,user_agent:str,
                     enable_network:bool=False,delay_seconds:float=1.0,
                     opener=None,sleeper=time.sleep)->dict[str,object]:
    planned=targets(ciks)
    if not enable_network:
        return {"state":"DRY_RUN_NO_REQUESTS","planned_urls":[url for _,url in planned],
                "price_feed":False,"automatic_scheduler":False,
                "owner_research_only":True}
    if (not isinstance(user_agent,str) or len(user_agent)>180 or
        len(user_agent.strip())<9 or "\n" in user_agent or "\r" in user_agent or
        not any(CONTACT_RE.fullmatch(x) for x in user_agent.split()) or
        not any(x for x in user_agent.split() if "@" not in x)):
        raise ValueError("real research organization/name and contact email required in SEC User-Agent")
    if type(delay_seconds) not in {int,float} or not 1.0<=delay_seconds<=120:
        raise ValueError("pacing is fixed at one SEC request per second or slower")
    if not isinstance(output,Path):raise TypeError("output directory must be Path")
    if output.resolve()==Path.cwd().resolve():raise ValueError("use a dedicated local output directory")
    output.mkdir(parents=True,exist_ok=True)
    opener=opener or _default_opener
    results=[]
    for index,(filename,url) in enumerate(planned):
        parsed=urlsplit(url)
        if parsed.scheme!="https" or parsed.hostname not in ALLOWED_HOSTS or parsed.username or parsed.password:
            raise ValueError("unapproved SEC host")
        if index:sleeper(delay_seconds)
        previous=_read_headers(output,filename)
        headers={"User-Agent":user_agent,"Accept":"application/json"}
        if previous.get("etag"):headers["If-None-Match"]=previous["etag"]
        if previous.get("last_modified"):headers["If-Modified-Since"]=previous["last_modified"]
        req=Request(url,headers=headers,method="GET")
        try:
            with opener(req,timeout=15) as response:
                final=urlsplit(response.geturl())
                if final.scheme!="https" or final.hostname not in ALLOWED_HOSTS or final.geturl()!=url:
                    raise ValueError("unexpected SEC redirect")
                raw=response.read(MAX_BYTES+1)
                if len(raw)>MAX_BYTES:raise ValueError("SEC response over explicit maximum size")
                payload=json.loads(raw)
                _validate_payload(filename,payload)
                # Atomic bounded cache replacement; no partially written approved data.
                tmp=output/f"{filename}.partial"
                normalized=json.dumps(payload,sort_keys=True)
                try:
                    tmp.write_text(normalized,encoding="utf-8")
                    tmp.replace(output/filename)
                finally:
                    tmp.unlink(missing_ok=True)
                metadata={"etag":response.headers.get("ETag",""),
                          "last_modified":response.headers.get("Last-Modified",""),
                          "retrieved_at":datetime.now(timezone.utc).isoformat(),
                          "url":url,"sha256":sha256(normalized.encode("utf-8")).hexdigest(),
                          "source_type":"PUBLIC_SEC_REFERENCE_NOT_QUOTE"}
                headtmp=output/f"{filename}.http-metadata.json.partial"
                try:
                    headtmp.write_text(json.dumps(metadata,sort_keys=True),encoding="utf-8")
                    headtmp.replace(_head_path(output,filename))
                finally:
                    headtmp.unlink(missing_ok=True)
                results.append({"file":filename,"state":"UPDATED","size_bytes":len(raw)})
        except HTTPError as exc:
            if exc.code==304 and (output/filename).exists():
                try:
                    cached=json.loads((output/filename).read_text(encoding="utf-8"))
                    _validate_payload(filename,cached)
                    metadata=json.loads(_head_path(output,filename).read_text(encoding="utf-8"))
                    if (metadata.get("url")!=url or
                        metadata.get("sha256")!=sha256((output/filename).read_bytes()).hexdigest()):
                        raise ValueError("cached SEC source identity or digest mismatch")
                    results.append({"file":filename,"state":"NOT_MODIFIED_VALID_CACHE"})
                except (OSError,ValueError,TypeError):
                    results.append({"file":filename,"state":"CACHE_HOLD"});break
            elif exc.code==429:
                results.append({"file":filename,"state":"RATE_LIMIT_HOLD_STOP",
                                "retry_after":exc.headers.get("Retry-After") if exc.headers else None})
                break
            else:
                results.append({"file":filename,"state":f"HTTP_HOLD_{exc.code}"});break
        except (URLError,ValueError,TimeoutError,OSError) as exc:
            # Provider error is redacted, no response body/header/token reflected.
            results.append({"file":filename,"state":"SOURCE_HOLD","error_type":type(exc).__name__})
            break
    healthy=all(x["state"] in {"UPDATED","NOT_MODIFIED_VALID_CACHE"} for x in results)
    return {"state":"PUBLIC_RESEARCH_SNAPSHOT" if healthy else "EDGAR_SOURCE_HOLD",
            "requests_attempted":len(results),"files":results,
            "source":"SEC EDGAR","price_feed":False,"real_time_market_data":False,
            "execution_ready":False,"automatic_scheduler":False,
            "filing_acceptance_is_intraday_header_verified":False}


def main()->None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",required=True,type=Path)
    parser.add_argument("--ciks",nargs="*",default=[])
    parser.add_argument("--user-agent",default="")
    parser.add_argument("--enable-network",action="store_true")
    args=parser.parse_args()
    print(json.dumps(fetch_public_sec(ciks=args.ciks,output=args.output,
         user_agent=args.user_agent,enable_network=args.enable_network),indent=2))


if __name__=="__main__":main()
