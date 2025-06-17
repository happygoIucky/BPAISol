import datetime
import hashlib
import hmac
import base64
import json
from urllib.parse import quote

import requests

# === CONFIGURATION ===
AK = "yourak"
SK = "yoursk"
#SK = base64.b64decode(SK_ENCODED).decode()

Service = "rtc"
Region = "ap-singapore-1"
Version = "2025-05-01"
Host = "open.byteplusapi.com"
ContentType = "application/json"


def norm_query(params):
    return "&".join(f"{quote(k, safe='-_.~')}={quote(v, safe='-_.~')}" for k, v in sorted(params.items()))


def hmac_sha256(key: bytes, content: str) -> bytes:
    return hmac.new(key, content.encode("utf-8"), hashlib.sha256).digest()


def hash_sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def sign_request(method: str, action: str, body_str: str):
    now = datetime.datetime.utcnow()
    x_date = now.strftime("%Y%m%dT%H%M%SZ")
    short_date = x_date[:8]

    query_params = {
        "Action": action,
        "Version": Version
    }
    canonical_query = norm_query(query_params)

    body_hash = hash_sha256(body_str)

    canonical_headers = (
        f"content-type:{ContentType}\n"
        f"host:{Host}\n"
        f"x-content-sha256:{body_hash}\n"
        f"x-date:{x_date}\n"
    )
    signed_headers = "content-type;host;x-content-sha256;x-date"

    canonical_request = "\n".join([
        method.upper(),
        "/",
        canonical_query,
        canonical_headers,
        signed_headers,
        body_hash
    ])

    hashed_canonical_request = hash_sha256(canonical_request)
    credential_scope = f"{short_date}/{Region}/{Service}/request"

    string_to_sign = "\n".join([
        "HMAC-SHA256",
        x_date,
        credential_scope,
        hashed_canonical_request
    ])

    k_date = hmac_sha256(SK.encode(), short_date)
    k_region = hmac_sha256(k_date, Region)
    k_service = hmac_sha256(k_region, Service)
    k_signing = hmac_sha256(k_service, "request")
    signature = hmac.new(k_signing, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

    authorization = (
        f"HMAC-SHA256 Credential={AK}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, Signature={signature}"
    )

    headers = {
        "content-type": ContentType,
        "host": Host,
        "x-content-sha256": body_hash,
        "x-date": x_date,
        "Authorization": authorization
    }

    return canonical_query, headers, body_str


if __name__ == "__main__":
    # === StartVoiceChat ASR-only Payload ===
    voicechat_payload = {
        "AppId": "yourappid",
        "RoomId": "youroomid",
        "TaskId": "randomname",
        "AgentConfig": {
            "TargetUserID": [
                "jl"
            ],
            "WelcomeMessage": "Hi, how can I help you today.",
            "UserID": "voicechat_jl"
        },

        "Config": {
            "ASRConfig": {
                "Provider": "amazon",
                "ProviderParams": {
                    "ID": "youramzid",
                    "Secret": "yoursecret",
                    "Region": "ap-southeast-1",
                    "Language": "en-US"
                },
                "VADConfig": {
                    "SilenceTime": 600
                },
                   "VolumeGain": 0.3
            },
            "TTSConfig": {
                "IgnoreBracketText": [
                    1,
                    2
                ],
                "Provider": "amazon",
                "ProviderParams": {
                    "ID": "youramzid",
                    "Secret": "yoursecret",
                    "VoiceID": "Celine",
                    "Region": "ap-southeast-1"
                }
            },

                "LLMConfig": {
                    "Mode": "BytePlusArk",
                    "EndPointId": "yourep",
                    "APIKey": "yourapikey",
                    "MaxTokens": 1024,
                    "Temperature": 0.1,
                    "TopP": 0.3,
                    "SystemMessage": "You are a helpful assistant.",
                    "UserPrompts": [
                        {
                            "Role": "user",
                            "Content": "Hello."
                        },
                        {
                            "Role": "assistant",
                            "Content": "What can I help you?"
                        }
                    ],
                    "HistoryLength": 3
                }
            }
        }
    
    voicechat_body = json.dumps(voicechat_payload, separators=(',', ':'))
    qs, hdrs, body = sign_request("POST", "StartVoiceChat", voicechat_body)

    print("\n=== ✅ CURL COMMAND: StartVoiceChat (ASR only) ===")
    print(f"curl -i -X POST 'https://{Host}/?{qs}' \\")
    for k, v in hdrs.items():
        print(f"  -H '{k}: {v}' \\")
    print(f"  -d '{body}'") 