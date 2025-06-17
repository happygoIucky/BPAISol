# 1. This script is catered for Conversational AI which requires you to have SSE protocol as well as some minor modification from the previous /chat to /chat/stream
# 2. Please refer to this and ensure that your RAG script is catered for this https://www.volcengine.com/docs/6348/1399966#%E4%B8%8B%E8%BD%BD%E5%92%8C%E4%BD%BF%E7%94%A8%E5%B7%A5%E5%85%B7
# 3. If you didn't validate 2.) you will not able to get response from Conversational AI
# 4. This script will be inline with template/index-ai.html so make sure when you run it, also replace the index accordingly.

import json
import requests
from volcengine.auth.SignerV4 import SignerV4
from volcengine.base.Request import Request
from volcengine.Credentials import Credentials

app = Flask(__name__)

# === CONFIG ===
collection_name = "pil_kb"
project_name = ""
ak = "yourak"
sk = "yoursk=="
g_knowledge_base_domain = "api-knowledgebase.mlp.cn-hongkong.bytepluses.com"
account_id = "yourid"

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
        "name": collection_name,
        "query": query,
        "limit": 20,
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


def chat_completion_stream(prompt, user_query):
    method = "POST"
    path = "/api/knowledge/chat/completions"
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": user_query}
    ]
    request_params = {
        "messages": messages,
        "stream": True,
        "return_token_usage": False,
        "model": "Skylark-pro",
        "temperature": 0.7
    }
    info_req = prepare_request(method, path, data=request_params)

    with requests.request(
        method=info_req.method,
        url=f"https://{g_knowledge_base_domain}{info_req.path}",
        headers=info_req.headers,
        data=info_req.body,
        stream=True
    ) as rsp:
        for line in rsp.iter_lines(decode_unicode=True):
            if not line:
                continue
            print("📡 Streaming line:", line)
            if line.startswith("data:"):
                try:
                    raw_json = line[len("data:"):].strip()
                    obj = json.loads(raw_json)
                    answer = obj.get("data", {}).get("generated_answer", "")
                    if answer:
                        formatted = {
                            "choices": [
                                {
                                    "delta": {
                                        "content": answer
                                    }
                                }
                            ]
                        }
                        yield f"data: {json.dumps(formatted)}\n\n"
                    if obj.get("data", {}).get("end"):
                        break
                except Exception as e:
                    print("❌ Parse error:", e, "| Raw line:", line)
        yield "data: [DONE]\n\n"

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
    try:
        result = rsp.json()
        return result.get("data", {}).get("generated_answer", "⚠️ No answer generated.")
    except Exception as e:
        return f"⚠️ Failed to parse response. Raw: {rsp.text}"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat_non_stream():
    user_query = request.json.get("query", "")
    kb_context = search_knowledge(user_query)
    prompt = base_prompt.format(kb_context)
    answer = chat_completion(prompt, user_query)
    return jsonify({"answer": answer})



@app.route("/chat/stream", methods=["POST"])
def chat_stream():
    data = request.get_json(silent=True)
    print("📥 Incoming JSON:", data)

    user_query = ""

    if data:
        # Check if OpenAI-style "messages" array is used
        if "messages" in data:
            messages = data.get("messages", [])
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    user_query = msg.get("content", "")
                    break
        else:
            # fallback to simpler { "query": "..." } format
            user_query = data.get("query", "")

    print("🔍 Extracted user query:", repr(user_query))

    if not user_query.strip():
        return Response("data: {\"error\": \"Empty query\"}\n\ndata: [DONE]\n\n", content_type="text/event-stream")

    kb_context = search_knowledge(user_query)
    prompt = base_prompt.format(kb_context)

    return Response(
        stream_with_context(chat_completion_stream(prompt, user_query)),
        content_type="text/event-stream"
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)