from __future__ import annotations

import json
import os
import sys
import urllib.request

base = os.environ.get('SIMPLEE_STAGING_BASE_URL', '').rstrip('/')
if not base:
    raise SystemExit('SIMPLEE_STAGING_BASE_URL is required')
url = base + '/tower/healthz'
with urllib.request.urlopen(url, timeout=15) as response:
    body = response.read().decode('utf-8')
    payload = json.loads(body)
    if response.status != 200 or payload.get('ok') is not True:
        raise SystemExit('managed staging health check failed')
print(json.dumps({'ok': True, 'health_url': url}, sort_keys=True))
