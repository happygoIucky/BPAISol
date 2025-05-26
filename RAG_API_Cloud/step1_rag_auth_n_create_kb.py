import json
import sys
import requests

from volcengine.auth.SignerV4 import SignerV4
from volcengine.base.Request import Request
from volcengine.Credentials import Credentials

AK = "youak"
SK = "yoursk"

def prepare_request(method, path, ak, sk, params=None, data=None, doseq=0):
    if params:
        for key in params:
            if (
                type(params[key]) == int
                or type(params[key]) == float
                or type(params[key]) == bool
            ):
                params[key] = str(params[key])
            elif type(params[key]) == list:
                if not doseq:
                    params[key] = ",".join(params[key])
    r = Request()
    r.set_shema("https")
    r.set_method(method)
    r.set_connection_timeout(10)
    r.set_socket_timeout(10)
    mheaders = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    r.set_headers(mheaders)
    if params:
        r.set_query(params)
    r.set_path(path)
    if data is not None:
        r.set_body(json.dumps(data))
    credentials = Credentials(ak, sk, "air", "cn-north-1")
    SignerV4.sign(r, credentials)
    return r


def create():
    method = "POST"
    path = "/api/knowledge/collection/create"
    request_params = {
        "name": "test",
        "data_type": "unstructured_data",
        "preprocessing": {
            "chunking_strategy": "custom_balance",
            "multi_modal": ["image_ocr"]
        },
        "index": {
            "cpu_quota": 1,
            "embedding_model": "bge-large-zh-and-m3",
            "embedding_dimension": 2048,
            "quant": "int8",
            "index_type": "hnsw_hybrid"
        },
    }

    info_req = prepare_request(method=method, path=path, ak=ak, sk=sk, data=request_params)
    rsp = requests.request(
    method = info_req.method,
    url = "https://{}{}".format(g_knowledge_base_domain,info_req.path),
    headers=info_req.headers,
    data=info_req.body
    )
    print(rsp.text)

if __name__ == "__main__":
    ak = "youak"
    sk = "yoursk=="
    g_knowledge_base_domain = "api-knowledgebase.mlp.cn-hongkong.bytepluses.com"
    account_id = "yourid"
    create()

