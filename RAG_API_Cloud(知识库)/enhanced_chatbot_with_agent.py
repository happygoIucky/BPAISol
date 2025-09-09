from flask import Flask, request, render_template, jsonify, session
import json
import requests
from volcengine.auth.SignerV4 import SignerV4
from volcengine.base.Request import Request
from volcengine.Credentials import Credentials
import uuid
from datetime import datetime
import threading
import time

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# === CONFIG ===
collection_name = "test"
project_name = ""
AK = "youak"
SK = "yoursk"
g_knowledge_base_domain = "api-knowledgebase.mlp.cn-hongkong.bytepluses.com"
account_id = "youraccountid"

base_prompt = """# Task
You are a helpful assistant. Answer accurately based on the context.
<context>
{}
</context>
"""

# === AGENT SYSTEM ===
# In-memory storage (in production, use Redis or database)
agent_queue = []  # List of chat sessions waiting for agent
active_agents = {}  # {agent_id: {session_id, name, status}}
chat_sessions = {}  # {session_id: {messages, status, agent_id, customer_info}}
agent_sessions = {}  # {agent_id: session_info}

class ChatSession:
    def __init__(self, session_id):
        self.session_id = session_id
        self.messages = []
        self.status = 'bot'  # 'bot', 'waiting_agent', 'with_agent', 'ended'
        self.agent_id = None
        self.created_at = datetime.now()
        self.customer_info = {}
        
    def add_message(self, sender, content, sender_type='user'):
        message = {
            'id': str(uuid.uuid4()),
            'sender': sender,
            'content': content,
            'sender_type': sender_type,  # 'user', 'bot', 'agent'
            'timestamp': datetime.now().isoformat()
        }
        self.messages.append(message)
        return message
        
    def to_dict(self):
        return {
            'session_id': self.session_id,
            'messages': self.messages,
            'status': self.status,
            'agent_id': self.agent_id,
            'created_at': self.created_at.isoformat(),
            'customer_info': self.customer_info
        }

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
    credentials = Credentials(AK, SK, "air", "cn-north-1")
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
    try:
        result = rsp.json()
        return result.get("data", {}).get("generated_answer", "⚠️ No answer generated.")
    except Exception as e:
        return f"⚠️ Failed to parse response. Raw: {rsp.text}"

def get_or_create_session(session_id=None):
    if not session_id:
        session_id = str(uuid.uuid4())
    
    if session_id not in chat_sessions:
        chat_sessions[session_id] = ChatSession(session_id)
    
    return chat_sessions[session_id]

def detect_agent_request(message):
    """Detect if user wants to talk to an agent"""
    agent_keywords = [
        'talk to agent', 'speak to agent', 'human agent', 'live agent',
        'customer service', 'support agent', 'real person', 'human help',
        'transfer to agent', 'escalate', 'speak to human'
    ]
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in agent_keywords)

# === ROUTES ===

@app.route("/")
def index():
    return render_template("enhanced_chatbot.html")

@app.route("/agent")
def agent_dashboard():
    return render_template("agent_dashboard.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_query = data.get("query", "")
    session_id = data.get("session_id") or session.get('session_id')
    
    # Get or create session
    chat_session = get_or_create_session(session_id)
    session['session_id'] = chat_session.session_id
    
    # Add user message
    chat_session.add_message("Customer", user_query, "user")
    
    # Check if user wants to talk to agent
    if detect_agent_request(user_query) and chat_session.status == 'bot':
        chat_session.status = 'waiting_agent'
        agent_queue.append(chat_session.session_id)
        
        response = "I understand you'd like to speak with a human agent. I'm connecting you now. Please wait a moment while I find an available agent to assist you."
        chat_session.add_message("System", response, "bot")
        
        return jsonify({
            "answer": response,
            "session_id": chat_session.session_id,
            "status": "waiting_agent",
            "queue_position": len(agent_queue)
        })
    
    # If already with agent, don't process with bot
    if chat_session.status == 'with_agent':
        return jsonify({
            "answer": "Your message has been sent to the agent. Please wait for their response.",
            "session_id": chat_session.session_id,
            "status": "with_agent"
        })
    
    # If waiting for agent, update queue position
    if chat_session.status == 'waiting_agent':
        queue_position = agent_queue.index(chat_session.session_id) + 1 if chat_session.session_id in agent_queue else 0
        return jsonify({
            "answer": f"You are currently in queue position {queue_position}. An agent will be with you shortly.",
            "session_id": chat_session.session_id,
            "status": "waiting_agent",
            "queue_position": queue_position
        })
    
    # Normal bot response
    kb_context = search_knowledge(user_query)
    prompt = base_prompt.format(kb_context)
    answer = chat_completion(prompt, user_query)
    
    # Add bot response
    chat_session.add_message("AI Assistant", answer, "bot")
    
    return jsonify({
        "answer": answer,
        "session_id": chat_session.session_id,
        "status": "bot"
    })

@app.route("/agent/login", methods=["POST"])
def agent_login():
    data = request.get_json()
    agent_name = data.get("name", "")
    agent_id = str(uuid.uuid4())
    
    active_agents[agent_id] = {
        "name": agent_name,
        "status": "available",
        "session_id": None,
        "login_time": datetime.now().isoformat()
    }
    
    session['agent_id'] = agent_id
    
    return jsonify({
        "agent_id": agent_id,
        "status": "logged_in",
        "queue_length": len(agent_queue)
    })

@app.route("/agent/pickup", methods=["POST"])
def agent_pickup():
    agent_id = session.get('agent_id')
    if not agent_id or agent_id not in active_agents:
        return jsonify({"error": "Agent not logged in"}), 401
    
    if not agent_queue:
        return jsonify({"error": "No customers in queue"}), 400
    
    # Get next customer from queue
    session_id = agent_queue.pop(0)
    chat_session = chat_sessions.get(session_id)
    
    if not chat_session:
        return jsonify({"error": "Session not found"}), 404
    
    # Assign agent to session
    chat_session.status = 'with_agent'
    chat_session.agent_id = agent_id
    active_agents[agent_id]['status'] = 'busy'
    active_agents[agent_id]['session_id'] = session_id
    
    # Add system message
    agent_name = active_agents[agent_id]['name']
    chat_session.add_message("System", f"Agent {agent_name} has joined the conversation.", "bot")
    
    return jsonify({
        "session_id": session_id,
        "customer_info": chat_session.customer_info,
        "messages": chat_session.messages,
        "status": "connected"
    })

@app.route("/agent/send", methods=["POST"])
def agent_send():
    agent_id = session.get('agent_id')
    if not agent_id or agent_id not in active_agents:
        return jsonify({"error": "Agent not logged in"}), 401
    
    data = request.get_json()
    message = data.get("message", "")
    session_id = active_agents[agent_id].get('session_id')
    
    if not session_id:
        return jsonify({"error": "No active session"}), 400
    
    chat_session = chat_sessions.get(session_id)
    if not chat_session:
        return jsonify({"error": "Session not found"}), 404
    
    # Add agent message
    agent_name = active_agents[agent_id]['name']
    chat_session.add_message(agent_name, message, "agent")
    
    return jsonify({"status": "sent", "message_id": chat_session.messages[-1]['id']})

@app.route("/agent/end", methods=["POST"])
def agent_end_session():
    agent_id = session.get('agent_id')
    if not agent_id or agent_id not in active_agents:
        return jsonify({"error": "Agent not logged in"}), 401
    
    session_id = active_agents[agent_id].get('session_id')
    if session_id:
        chat_session = chat_sessions.get(session_id)
        if chat_session:
            chat_session.status = 'ended'
            chat_session.add_message("System", "Agent has ended the conversation. Thank you for contacting us!", "bot")
    
    # Reset agent status
    active_agents[agent_id]['status'] = 'available'
    active_agents[agent_id]['session_id'] = None
    
    return jsonify({"status": "session_ended"})

@app.route("/agent/status")
def agent_status():
    agent_id = session.get('agent_id')
    if not agent_id or agent_id not in active_agents:
        return jsonify({"error": "Agent not logged in"}), 401
    
    agent_info = active_agents[agent_id]
    session_id = agent_info.get('session_id')
    
    response = {
        "agent_info": agent_info,
        "queue_length": len(agent_queue),
        "active_agents_count": len([a for a in active_agents.values() if a['status'] == 'available'])
    }
    
    if session_id:
        chat_session = chat_sessions.get(session_id)
        if chat_session:
            response['current_session'] = chat_session.to_dict()
    
    return jsonify(response)

@app.route("/session/messages/<session_id>")
def get_session_messages(session_id):
    chat_session = chat_sessions.get(session_id)
    if not chat_session:
        return jsonify({"error": "Session not found"}), 404
    
    return jsonify({
        "messages": chat_session.messages,
        "status": chat_session.status,
        "agent_id": chat_session.agent_id
    })

@app.route("/admin/stats")
def admin_stats():
    return jsonify({
        "total_sessions": len(chat_sessions),
        "queue_length": len(agent_queue),
        "active_agents": len(active_agents),
        "available_agents": len([a for a in active_agents.values() if a['status'] == 'available']),
        "busy_agents": len([a for a in active_agents.values() if a['status'] == 'busy'])
    })

if __name__ == "__main__":
    print("🚀 Enhanced Chatbot with Agent Support Starting...")
    print("📱 Customer Interface: http://localhost:5000/")
    print("👨‍💼 Agent Dashboard: http://localhost:5000/agent")
    print("📊 Admin Stats: http://localhost:5000/admin/stats")
    app.run(host="0.0.0.0", port=5000, debug=True)