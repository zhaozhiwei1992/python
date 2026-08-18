#!/usr pip install requests
import requests
from requests.auth import HTTPBasicAuth

NEXUS = "http://10.11.12.164:28081"
AUTH = HTTPBasicAuth("admin", "YJcJzDT6zDTgQE")
HOSTED_REPO = "maven-releases"   # 你当时传的那个 hosted 仓库，别填 maven-public

# 这些 group 前缀全是从 Central / Spring / Apache 来的开源包，必须删
OPEN_SOURCE_GROUPS = [
    "org.springframework",
    "org.springframework.boot",
    "org.springframework.cloud",
    "org.apache.commons",
    "org.apache.shiro",
    "com.baomidou",
    "com.fasterxml.jackson",
    "com.squareup.okhttp3",
    "com.atomikos",
    "com.sun.mail",
    "javax.mail",
    "commons-codec",
    "commons-io",
    "org.openeuler",
]

def fetch_and_delete():
    cont = None
    total = 0
    while True:
        url = f"{NEXUS}/service/rest/v1/components?repository={HOSTED_REPO}"
        if cont:
            url += f"&continuationToken={cont}"
        r = requests.get(url, auth=AUTH, timeout=60)
        r.raise_for_status()
        data = r.json()
        items = data.get("items", [])
        for c in items:
            g = c.get("group", "")
            if any(g == prefix or g.startswith(prefix + ".") for prefix in OPEN_SOURCE_GROUPS):
                cid = c["id"]
                del_r = requests.delete(
                    f"{NEXUS}/service/rest/v1/components/{cid}",
                    auth=AUTH,
                    timeout=60,
                )
                total += 1
                print(f"deleted [{del_r.status_code}] {g}:{c.get('name')}:{c.get('version')}")
        cont = data.get("continuationToken")
        if not cont:
            break
    print(f"\n=== total deleted: {total} ===")

if __name__ == "__main__":
    # 先 dry-run 可以把下面这行注释掉 DELETE 只打印，确认无误再放开
    fetch_and_delete()
