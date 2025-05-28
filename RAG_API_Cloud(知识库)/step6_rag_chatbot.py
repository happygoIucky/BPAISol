from flask import Flask, request, render_template, jsonify
import json
import requests
from volcengine.auth.SignerV4 import SignerV4
from volcengine.base.Request import Request
from volcengine.Credentials import Credentials

app = Flask(__name__)

# === CONFIG ===
collection_name = "test"
project_name = ""
AK = "youak"
SK = "yoursk"
g_knowledge_base_domain = "api-knowledgebase.mlp.cn-hongkong.bytepluses.com"
account_id = "youraccountid"


base_prompt = """# Task\nYou are a helpful assistant. Answer accurately based on the context.\n<context>\n{}\n</context>\n"""

def prepare_request(method, path, params=None, data=None, doseq=0):
    r = Request()
    r.set_shema("https")
    r.set_method(method)
    r.set_connection_timeout(10)
    r.set_socket_timeout(10)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8",
        "Host": g_knowledge_base_domain,
        "V-Account-Id": account_id,
    }
    r.set_headers(headers)
    if params:
        r.set_query(params)
    r.set_host(g_knowledge_base_domain)
    r.set_path(path)
    if data is not None:
        r.set_body(json.dumps(data))
    credentials = Credentials(ak, sk, "air", "cn-north-1")
    SignerV4.sign(r, credentials)
    return r

def search_knowledge(query):
    method = "POST"
    path = "/api/knowledge/collection/search_knowledge"
    request_params = {
        "project": "",
        "name": "test",
        "query": query,
        "limit": 5,
        "pre_processing": {
            "need_instruction": False,
            "rewrite": False,
            "return_token_usage": False
        },
        "dense_weight": 0.5,
        "post_processing": {
            "chunk_group": True,
            "rerank_switch": False
        }
    }
    info_req = prepare_request(method, path, data=request_params)
    rsp = requests.request(
        method=info_req.method,
        url=f"https://{g_knowledge_base_domain}{info_req.path}",
        headers=info_req.headers,
        data=info_req.body
    )
    print("🔍 KB Search Response:", rsp.text)
    data = rsp.json()
    chunks = data.get("data", {}).get("result_list", [])
    return "\n".join([c.get("content", "") for c in chunks])

def chat_completion(prompt, user_query):
    method = "POST"
    path = "/api/knowledge/chat/completions"
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": user_query}
    ]
    request_params = {
        "messages": messages,
        "stream": False,
        "return_token_usage": True,
        "model": "Skylark-pro",
        "max_tokens": 1024,
        "temperature": 0.7
    }
    info_req = prepare_request(method, path, data=request_params)
    rsp = requests.request(
        method=info_req.method,
        url=f"https://{g_knowledge_base_domain}{info_req.path}",
        headers=info_req.headers,
        data=info_req.body
    )
    #print("🤖 Chat Completion Response:", rsp.text)
    resp_json = rsp.json()
    print(json.dumps(resp_json, indent=2))
    try:
        result = rsp.json()
        return result.get("data", {}).get("generated_answer", "⚠️ No answer generated.")
    except Exception as e:
        return f"⚠️ Failed to parse response. Raw: {rsp.text}"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_query = request.json.get("query", "")
    kb_context = search_knowledge(user_query)
    prompt = base_prompt.format(kb_context)
    answer = chat_completion(prompt, user_query)
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

