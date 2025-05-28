import requests 
from step1_volc_auth_n_create_collection import prepare_request 
# Note: If `volc_auth` is highlighted in red and an error occurs, do not use `pip install volc_auth`. 
# This is because `volc_auth.py` is not an installation package, but a local Python file. 
# Make sure that you have saved the `volc_auth.py` file (refer to the "Preparation" topic) in the same directory as the following code. 
# For more information, refer to the "3. Construct and save a signature generation function (in Python)" section in the "Preparation" topic. 

AK = "youak"
SK = "yoursk"

DOMAIN = "api-vikingdb.mlp.ap-mya.byteplus.com" 

# Query data in a collection. 
request_params = {"collection_name": "your_collection", "primary_keys": 1} 

# Call the prepare_request function to generate a request and add a signature. 
info_collection_req = prepare_request( 
    method="GET", 
    path="/api/collection/fetch_data", 
    ak=AK, 
    sk=SK, 
    data=request_params, 
) 
# Complete the request. 
r = requests.request( 
    method=info_collection_req.method, 
    url="https://{}{}".format(DOMAIN, info_collection_req.path), 
    headers=info_collection_req.headers, 
    data=info_collection_req.body, 
) 

# Print the response. 
print(r.text)
