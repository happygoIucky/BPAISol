import json
import base64
import datetime
import hashlib
import hmac
from urllib.parse import quote
import requests

# === CONFIGURATION ===
Service = "filenas"
Version = "2022-01-01"
Region = "ap-southeast-1"
Host = "open.ap-southeast-1.byteplusapi.com"
ContentType = "application/json; charset=utf-8"

AK = "yourak"
SK = "yoursk"

# === UTILITIES ===
def norm_query(params):
    query = ""
    for key in sorted(params.keys()):
        if isinstance(params[key], list):
            for k in params[key]:
                query += quote(key, safe="-_.~") + "=" + quote(k, safe="-_.~") + "&"
        else:
            query += quote(key, safe="-_.~") + "=" + quote(str(params[key]), safe="-_.~") + "&"
    return query[:-1].replace("+", "%20")

def hmac_sha256(key: bytes, content: str):
    return hmac.new(key, content.encode("utf-8"), hashlib.sha256).digest()

def hash_sha256(content: str):
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

# === SIGNED REQUEST ===
def request(method, date, query, header, ak, sk, action, body):
    credential = {
        "access_key_id": ak,
        "secret_access_key": sk,
        "service": Service,
        "region": Region,
    }

    request_param = {
        "body": body or "",
        "host": Host,
        "path": "/",
        "method": method,
        "content_type": ContentType,
        "date": date,
        "query": {"Action": action, "Version": Version, **query},
    }

    x_date = request_param["date"].strftime("%Y%m%dT%H%M%SZ")
    short_x_date = x_date[:8]
    x_content_sha256 = hash_sha256(request_param["body"])

    signed_headers_str = ";".join([
        "content-type", "host", "x-content-sha256", "x-date"
    ])

    canonical_request_str = "\n".join([
        request_param["method"].upper(),
        request_param["path"],
        norm_query(request_param["query"]),
        "\n".join([
            f"content-type:{request_param['content_type']}",
            f"host:{request_param['host']}",
            f"x-content-sha256:{x_content_sha256}",
            f"x-date:{x_date}"
        ]),
        "",
        signed_headers_str,
        x_content_sha256
    ])

    hashed_canonical_request = hash_sha256(canonical_request_str)
    credential_scope = "/".join([short_x_date, credential["region"], credential["service"], "request"])
    string_to_sign = "\n".join(["HMAC-SHA256", x_date, credential_scope, hashed_canonical_request])

    k_date = hmac_sha256(credential["secret_access_key"].encode("utf-8"), short_x_date)
    k_region = hmac_sha256(k_date, credential["region"])
    k_service = hmac_sha256(k_region, credential["service"])
    k_signing = hmac_sha256(k_service, "request")
    signature = hmac_sha256(k_signing, string_to_sign).hex()

    auth_header = {
        "Authorization": f"HMAC-SHA256 Credential={credential['access_key_id']}/{credential_scope}, SignedHeaders={signed_headers_str}, Signature={signature}",
        "Host": request_param["host"],
        "X-Content-Sha256": x_content_sha256,
        "X-Date": x_date,
        "Content-Type": request_param["content_type"]
    }

    full_header = {**header, **auth_header}

    url = f"https://{request_param['host']}{request_param['path']}"
    response = requests.request(
        method=method,
        url=url,
        headers=full_header,
        params=request_param["query"],
        data=request_param["body"]
    )
    return response.json()

# === EXECUTION ===
if __name__ == "__main__":
    now = datetime.datetime.utcnow()

    body = json.dumps({
        "FileSystemName": "yourfsname",
        "ZoneId": "ap-southeast-1b",
        "Description": "Just-for-test",
        "ChargeType": "PayAsYouGo",
        "FileSystemType": "Extreme",
        "StoreType": "Standard",
        "ProtocolType": "NFS",
        "ProjectName": "default",
        "Capacity": 100
    }, separators=(',', ':'))

    res = request("POST", now, {}, {}, AK, SK, "CreateFileSystem", body)
    print("=== CreateFileSystem ===")
    print(json.dumps(res, indent=2))
