"""No real public HTTP requests; mock opt-in SEC collector's transport."""
from email.message import Message
from urllib.error import HTTPError
import json

import pytest

from scripts.obscan_public_edgar_fetch import fetch_public_sec, targets


class Reply:
    def __init__(self,url,payload,etag=""):
        self.url=url
        self.payload=json.dumps(payload).encode()
        self.headers={"ETag":etag,"Last-Modified":"Mon, 28 Sep 2026 00:00:00 GMT"}
    def __enter__(self):return self
    def __exit__(self,*unused):return None
    def geturl(self):return self.url
    def read(self,amount):return self.payload[:amount]


def test_default_dry_run_has_zero_requests(tmp_path):
    def forbidden(*args,**kwargs):raise AssertionError("dry-run opened a network connection")
    report=fetch_public_sec(ciks=["0000320193"],output=tmp_path,user_agent="",opener=forbidden)
    assert report["state"]=="DRY_RUN_NO_REQUESTS"
    assert len(report["planned_urls"])==2
    assert not tmp_path.joinpath("company_tickers_exchange.json").exists()


def test_bounds_and_contact_are_required(tmp_path):
    with pytest.raises(ValueError):targets(["ABC"])
    with pytest.raises(ValueError):targets(["123"]*21)
    with pytest.raises(ValueError):
        fetch_public_sec(ciks=["123"],output=tmp_path,user_agent="unidentified",enable_network=True)
    with pytest.raises(ValueError):
        fetch_public_sec(ciks=["123"],output=tmp_path,user_agent="Research a@b.com",
                         enable_network=True,delay_seconds=0.25)
    assert targets(["123","0000000123"])[1:]==[
        ("CIK0000000123.json","https://data.sec.gov/submissions/CIK0000000123.json")]


def test_owner_opt_in_has_identified_bounded_approved_requests(tmp_path):
    seen,slept=[],[]
    def opener(req,timeout=0):
        seen.append((req.full_url,req.get_header("User-agent"),timeout))
        return Reply(req.full_url,{"status":"public-metadata"},"meta-etag")
    report=fetch_public_sec(ciks=["123"],output=tmp_path,user_agent="Simplee Research contact@example.org",
                            enable_network=True,opener=opener,sleeper=slept.append)
    assert report["state"]=="PUBLIC_METADATA_ONLY"
    assert report["requests_attempted"]==2
    assert len(seen)==2 and slept==[1.0]
    assert all(host.startswith("https://www.sec.gov/") or host.startswith("https://data.sec.gov/")
               for host,_,_ in seen)
    assert all(agent=="Simplee Research contact@example.org" and timeout==15 for _,agent,timeout in seen)
    assert json.loads((tmp_path/"CIK0000000123.json").read_text())["status"]=="public-metadata"
    assert report["real_time_market_data"] is False and report["execution_ready"] is False


def test_public_rate_limit_stops_without_bypass(tmp_path):
    def too_many(req,timeout=0):
        headers=Message()
        headers["Retry-After"]="60"
        raise HTTPError(req.full_url,429,"too many",headers,None)
    report=fetch_public_sec(ciks=["123","124"],output=tmp_path,
          user_agent="Research contact@example.org",enable_network=True,opener=too_many)
    assert report["requests_attempted"]==1
    assert report["files"][0]["state"]=="RATE_LIMIT_HOLD_STOP"
    assert not (tmp_path/"CIK0000000123.json").exists()


def test_host_redirect_and_invalid_json_cannot_overwrite_files(tmp_path):
    saved=tmp_path/"company_tickers_exchange.json"
    saved.write_text('{"previous":true}')
    def redirected(req,timeout=0):return Reply("https://unapproved.invalid/",{})
    report=fetch_public_sec(ciks=[],output=tmp_path,user_agent="Research contact@example.org",
                             enable_network=True,opener=redirected)
    assert report["files"][0]["state"]=="SOURCE_HOLD"
    assert json.loads(saved.read_text())=={"previous":True}
    def broken(req,timeout=0):return Reply(req.full_url,["not an expected JSON object"])
    report=fetch_public_sec(ciks=[],output=tmp_path,user_agent="Research contact@example.org",
                             enable_network=True,opener=broken)
    assert report["files"][0]["state"]=="SOURCE_HOLD"
    assert json.loads(saved.read_text())=={"previous":True}
