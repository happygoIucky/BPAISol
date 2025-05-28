import json 
import requests 

from volcengine.auth.SignerV4 import SignerV4 
from volcengine.base.Request import Request 
from volcengine.Credentials import Credentials 

collection_name = "test" #Knowledge base name 
project_name = "" 

query = "Explain the firewall for LLM in details?" #Current question 

AK = "youak"
SK = "yoursk"
g_knowledge_base_domain = "api-knowledgebase.mlp.cn-hongkong.bytepluses.com"
account_id = "youraccountid"

base_prompt = """# Task 
You are an online customer service agent. Your primary task is to skillfully respond to user's questions using tactful language. You need to answer the following questions based on the reference materials provided within the <context></context> XML tags. Your answers should be accurate and concise. 

Your answers should meet the following requirements: 
    1. The answer must be within the scope of the reference materials. Answer the question as concisely as possible, and do not provide any explanations beyond the reference materials. 
    2. The answer must be generated based on the questions and reference materials. Maintain friendly communication with the user. 
    3. If the reference materials cannot help you answer the question, inform the user that the question cannot be answered and guide him or her to provide more detailed information. 
    4. For confidentiality reasons, politely decline to answer questions about the document names or authors of the reference materials. 

# Task execution 
Now, answer the question based on the provided reference materials while adhering to the constraints. Your answer must be accurate and complete. 

# Reference materials 
<context> 
  {} 
</context> 
""" 

def prepare_request(method, path, params=None, data=None, doseq=0): 
    if params: 
        for key in params: 
            if ( 
                    isinstance(params[key], int) 
                    or isinstance(params[key], float) 
                    or isinstance(params[key], bool) 
            ): 
                params[key] = str(params[key]) 
            elif isinstance(params[key], list): 
                if not doseq: 
                    params[key] = ",".join(params[key]) 
    r = Request() 
    r.set_shema("http") 
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

    # Signature generation 
    credentials = Credentials(ak, sk, "air", "cn-north-1") 
    SignerV4.sign(r, credentials) 
    return r 


def search_knowledge(): 
    method = "POST" 
    path = "/api/knowledge/collection/search_knowledge" #Knowledge base retrieval 
    request_params = { 
    "project": "", 
    "name": "test", 
    "query": "What is the development friendly in this document", 
    "limit": 10, 
    "pre_processing": { 
        "need_instruction": True, #Specifies whether to concatenate instructions, recommended for asymmetric questions 
        "rewrite": False, #Multi-turn rewriting switch, only rewrites the current question based on messages 
        "return_token_usage": True, 
        "messages": [ 
            { 
                "role": "system", 
                "content": "" 
            }, 
            { 
                "role": "user", 
                "content": query 
            } 
        ] 
    }, 
    "dense_weight": 0.5, #Adjust the weight of semantic retrieval. 1 represents pure semantic retrieval, and this only takes effect when the vectorization model selects the semantic + keyword model 
    "post_processing": { 
        "get_attachment_link": True, #Specifies whether to return the original image, and this only takes effect when OCR is enabled during knowledge base creation; otherwise, images are automatically skipped 
        "chunk_group": True, #Specifies whether to aggregate retrieved chunks by document 
        "rerank_only_chunk": False, #Specifies whether to rerank retrieved chunks according to the document word order 
        "rerank_switch": False, #Specifies whether to enable reranking 
        "chunk_diffusion_count": 0 #Specifies whether to retrieve adjacent chunks. For example, 1 represents retrieving one additional chunk before and after the current chunk 
    } 
} 

    info_req = prepare_request(method=method, path=path, data=request_params) 
    rsp = requests.request( 
        method=info_req.method, 
        url="http://{}{}".format(g_knowledge_base_domain, info_req.path), 
        headers=info_req.headers, 
        data=info_req.body 
    ) 
    # print("search res = {}".format(rsp.text)) 
    return rsp.text 

def chat_completion(message, stream=False, return_token_usage=True, temperature=0.7, max_tokens=4096): 
    method = "POST" 
    path = "/api/knowledge/chat/completions" #LLM generation 
    request_params = { 
        "messages": message, #Pass the prompt, retrieved chunks, and historical multi-turn dialogue through the messages field 
        "stream": True, #Specifies whether it is streaming response 
        "return_token_usage": True, 
        "model": "Skylark-pro", #By default, this model uses the public endpoint of the system. To use a private endpoint created on ModelArk, pass ep_id here and specify the api_key parameter. For more information, refer to chat_completions. 
        "max_tokens": 4096, 
        "temperature": 0.7
    } 

    info_req = prepare_request(method=method, path=path, data=request_params) 
    rsp = requests.request( 
        method=info_req.method, 
        url="http://{}{}".format(g_knowledge_base_domain, info_req.path), 
        headers=info_req.headers, 
        data=info_req.body 
    ) 
    print("chat completion res = {}".format(rsp.text)) 

def generate_prompt(rsp_txt): # System prompt concatenation 
    rsp = json.loads(rsp_txt) 
    if rsp["code"] != 0: 
        return 
    prompt = "" 
    rsp_data = rsp["data"] 
    points = rsp_data["result_list"] 

    for point in points: 
        # System field concatenated first 
        doc_info = point["doc_info"] 
        for system_field in ["doc_name","title","chunk_title","content"] : 
            if system_field == 'doc_name' or system_field == 'title': 
                if system_field in doc_info: 
                    prompt += f"{system_field}: {doc_info[system_field]}\n" 
            else: 
                if system_field in point: 
                    if system_field == "content" and doc_info["doc_type"] == "faq.xlsx": 
                        question_field = "original_question" 
                        prompt += f"content: When a similar question is asked, refer to the corresponding answer: Question: {point[question_field]}; Answer: {point[system_field]}\n" #FAQ best practices 
                    else: 
                        prompt += f"{system_field}: {point[system_field]}\n" 
        if "table_chunk_fields" in point: 
            table_chunk_fields = point["table_chunk_fields"] 
            for self_field in [] : 
                # Use next() to find the first project that matches the condition from table_chunk_fields 
                find_one = next((item for item in table_chunk_fields if item["field_name"] == self_field), None) 
                if find_one: 
                    prompt += f"{self_field}: {find_one['field_value']}\n" 

        prompt += "---\n" 

    return base_prompt.format(prompt) 

def search_knowledge_and_chat_completion(): 
    # 1. search_knowledge execution 
   rsp_txt = search_knowledge() 
    # 2. Prompt generation 
   prompt = generate_prompt(rsp_txt) 
    # todo: Users need to cache dialogue information locally and sequentially add it to messages 
    # 3. Dialogue concatenation, where the question corresponds to the role user, the system corresponds to the role system, the answer corresponds to the role assistant, and the content corresponds to content 
   messages =[ 
       { 
           "role": "system", 
           "content": prompt  #LLM instruction + retrieval result test
       }, 
       { 
           "role": "user", 
           "content": query 
       } 
   ] 

    # 4. chat_completion calling 
   chat_completion(messages) 

if __name__ == "__main__": 
    search_knowledge_and_chat_completion()
