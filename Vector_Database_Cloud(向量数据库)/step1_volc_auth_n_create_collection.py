# volc_auth.py 

import json 
import sys 
import requests 

from volcengine.auth.SignerV4 import SignerV4 
from volcengine.base.Request import Request 
from volcengine.Credentials import Credentials 


def prepare_request(method, path, ak, sk, params=None, data=None, doseq=0): 
    if params: 
        for key in params: 
            if ( 
                type(params[key]) == int 
                or type(params[key]) == float 
                or type(params[key]) == bool 
            ): 
                params[key] = str(params[key]) 
            elif sys.version_info[0] != 3: 
                if type(params[key]) == unicode: 
                    params[key] = params[key].encode("utf-8") 
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
        "Host": "api-vikingdb.mlp.ap-mya.byteplus.com", 
    } 
    r.set_headers(mheaders) 
    if params: 
        r.set_query(params) 
    r.set_host("api-vikingdb.mlp.ap-mya.byteplus.com") 
    r.set_path(path) 
    if data is not None: 
        r.set_body(json.dumps(data)) 
    # Generate a signature. 
    credentials = Credentials(ak, sk, "air", "ap-southeast-1") 
    SignerV4.sign(r, credentials) 
    return r


AK = "youak"
SK = "yoursk"

DOMAIN = "api-vikingdb.mlp.ap-mya.byteplus.com"

# Create a collection.
request_params = {
    "collection_name": "your_collection",
    "description": "This is a use case that describes how to use the prepare_request function to generate a signature and create a collection in Vector Databese.",
    # Set a primary key.
    "primary_key": "id",
    # Specify fields.
    "fields": [
        {
            "field_name": "id",
            "field_type": "int64",
        },
        {"field_name": "vector_field", "field_type": "vector", "dim": 64}
        # Specify other fields as you need.
    ],
}

# Call the prepare_request function to generate a request and add a signature.
info_collection_req = prepare_request(
    method="POST",
    path="/api/collection/create",
    ak=AK,
    sk=SK,
    data=request_params,
)
# Complete the request.
r = requests.request(
    method=info_collection_req.method,
    url="https://{}{}".format(DOMAIN, info_collection_req.path),
    headers=info_collection_req.headers,
    params=info_collection_req.query,
    data=info_collection_req.body,
)

# Print the response.
print(r.text)
