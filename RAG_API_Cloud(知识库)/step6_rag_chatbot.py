from flask import Flask, request, render_template, jsonify
import json
import requests
from volcengine.auth.SignerV4 import SignerV4
from volcengine.base.Request import Request
from volcengine.Credentials import Credentials
import time
import hashlib
import hmac
import base64
from urllib.parse import urlencode
from datetime import datetime
import uuid
import threading
from collections import defaultdict

app = Flask(__name__)

# === CONFIG ===
collection_name = "test"
project_name = ""
AK = "youak"
SK = "yoursk"
g_knowledge_base_domain = "api-knowledgebase.mlp.cn-hongkong.bytepluses.com"
account_id = "youraccountid"


base_prompt = """# Task\nYou are a helpful assistant. Answer accurately based on the context.\n<context>\n{}\n</context>\n"""

# Agent handoff system
class ChatSession:
    def __init__(self, session_id):
        self.session_id = session_id
        self.status = 'bot'  # bot, waiting_agent, with_agent, ended
        self.messages = []
        self.agent_id = None
        self.created_at = datetime.now()
        self.agent_requested_at = None
        self.agent_connected_at = None
        
    def add_message(self, sender, content, sender_type='user'):
        message = {
            'sender': sender,
            'content': content,
            'sender_type': sender_type,
            'timestamp': datetime.now().isoformat()
        }
        self.messages.append(message)
        return message
        
    def request_agent(self):
        self.status = 'waiting_agent'
        self.agent_requested_at = datetime.now()
        
    def assign_agent(self, agent_id):
        self.agent_id = agent_id
        self.status = 'with_agent'
        self.agent_connected_at = datetime.now()
        
    def end_session(self):
        self.status = 'ended'
        self.agent_id = None

# Global storage (in production, use Redis or database)
sessions = {}
agent_queue = []  # List of session_ids waiting for agents
active_agents = {}  # agent_id -> {name, status, current_sessions}
session_lock = threading.Lock()

def get_or_create_session(session_id=None):
    if not session_id:
        session_id = str(uuid.uuid4())
    
    with session_lock:
        if session_id not in sessions:
            sessions[session_id] = ChatSession(session_id)
        return sessions[session_id]

def detect_agent_request(query):
    """Detect if user wants to talk to an agent"""
    agent_keywords = [
        'talk to agent', 'human agent', 'speak to agent', 'connect to agent',
        'customer service', 'customer support', 'live chat', 'human help',
        'representative', 'operator', 'real person', 'human assistance'
    ]
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in agent_keywords)

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

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_query = data.get('query', '')
    session_id = data.get('session_id')
    
    if not user_query:
        return jsonify({'error': 'No query provided'}), 400
    
    try:
        # Get or create session
        session = get_or_create_session(session_id)
        
        # Add user message to session
        session.add_message('customer', user_query, 'user')
        
        # Check if user wants to talk to an agent
        if detect_agent_request(user_query) and session.status == 'bot':
            session.request_agent()
            with session_lock:
                if session.session_id not in agent_queue:
                    agent_queue.append(session.session_id)
            
            queue_position = agent_queue.index(session.session_id) + 1
            response_message = f"I understand you'd like to speak with a human agent. You've been added to the queue at position {queue_position}. An agent will be with you shortly."
            session.add_message('system', response_message, 'system')
            
            return jsonify({
                'answer': response_message,
                'session_id': session.session_id,
                'status': session.status,
                'queue_position': queue_position
            })
        
        # If session is with agent, don't process with AI
        if session.status == 'with_agent':
            response_message = "You are currently connected with an agent. Please wait for their response."
            return jsonify({
                'answer': response_message,
                'session_id': session.session_id,
                'status': session.status,
                'agent_name': active_agents.get(session.agent_id, {}).get('name', 'Agent')
            })
        
        # If waiting for agent
        if session.status == 'waiting_agent':
            queue_position = agent_queue.index(session.session_id) + 1 if session.session_id in agent_queue else 0
            response_message = f"You are still in the queue at position {queue_position}. An agent will be with you shortly."
            return jsonify({
                'answer': response_message,
                'session_id': session.session_id,
                'status': session.status,
                'queue_position': queue_position
            })
        
        # Normal AI processing
        kb_context = search_knowledge(user_query)
        prompt = base_prompt.format(kb_context)
        answer = chat_completion(prompt, user_query)
        
        # Add AI response to session
        session.add_message('assistant', answer, 'bot')
        
        return jsonify({
            'answer': answer,
            'session_id': session.session_id,
            'status': session.status,
            'knowledge_used': kb_context
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Agent management routes
@app.route('/agent/login', methods=['POST'])
def agent_login():
    data = request.get_json()
    agent_name = data.get('agent_name')
    
    if not agent_name:
        return jsonify({'error': 'Agent name required'}), 400
    
    agent_id = str(uuid.uuid4())
    active_agents[agent_id] = {
        'name': agent_name,
        'status': 'available',
        'current_sessions': [],
        'login_time': datetime.now().isoformat()
    }
    
    return jsonify({
        'agent_id': agent_id,
        'message': f'Agent {agent_name} logged in successfully'
    })

@app.route('/agent/pickup', methods=['POST'])
def agent_pickup():
    data = request.get_json()
    agent_id = data.get('agent_id')
    session_id = data.get('session_id')
    
    if not agent_id or not session_id:
        return jsonify({'error': 'Agent ID and Session ID required'}), 400
    
    if agent_id not in active_agents:
        return jsonify({'error': 'Agent not found'}), 404
    
    if session_id not in sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    session = sessions[session_id]
    
    with session_lock:
        # Remove from queue
        if session_id in agent_queue:
            agent_queue.remove(session_id)
        
        # Assign agent
        session.assign_agent(agent_id)
        active_agents[agent_id]['current_sessions'].append(session_id)
        active_agents[agent_id]['status'] = 'busy'
    
    # Add system message
    agent_name = active_agents[agent_id]['name']
    session.add_message('system', f'Agent {agent_name} has joined the chat.', 'system')
    
    return jsonify({
        'message': 'Session picked up successfully',
        'session_id': session_id,
        'agent_name': agent_name
    })

@app.route('/agent/send', methods=['POST'])
def agent_send_message():
    data = request.get_json()
    agent_id = data.get('agent_id')
    session_id = data.get('session_id')
    message = data.get('message')
    
    if not all([agent_id, session_id, message]):
        return jsonify({'error': 'Agent ID, Session ID, and message required'}), 400
    
    if agent_id not in active_agents:
        return jsonify({'error': 'Agent not found'}), 404
    
    if session_id not in sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    session = sessions[session_id]
    
    if session.agent_id != agent_id:
        return jsonify({'error': 'Agent not assigned to this session'}), 403
    
    # Add agent message
    agent_name = active_agents[agent_id]['name']
    session.add_message(agent_name, message, 'agent')
    
    return jsonify({'message': 'Message sent successfully'})

@app.route('/agent/end', methods=['POST'])
def agent_end_session():
    data = request.get_json()
    agent_id = data.get('agent_id')
    session_id = data.get('session_id')
    
    if not agent_id or not session_id:
        return jsonify({'error': 'Agent ID and Session ID required'}), 400
    
    if agent_id not in active_agents:
        return jsonify({'error': 'Agent not found'}), 404
    
    if session_id not in sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    session = sessions[session_id]
    
    with session_lock:
        # End session
        session.end_session()
        
        # Remove from agent's current sessions
        if session_id in active_agents[agent_id]['current_sessions']:
            active_agents[agent_id]['current_sessions'].remove(session_id)
        
        # Update agent status
        if not active_agents[agent_id]['current_sessions']:
            active_agents[agent_id]['status'] = 'available'
    
    # Add system message
    session.add_message('system', 'Chat session ended by agent.', 'system')
    
    return jsonify({'message': 'Session ended successfully'})

@app.route('/agent/status')
def agent_status():
    agent_id = request.args.get('agent_id')
    
    if not agent_id:
        return jsonify({'error': 'Agent ID required'}), 400
    
    if agent_id not in active_agents:
        return jsonify({'error': 'Agent not found'}), 404
    
    agent = active_agents[agent_id]
    return jsonify({
        'agent_id': agent_id,
        'name': agent['name'],
        'status': agent['status'],
        'current_sessions': len(agent['current_sessions']),
        'login_time': agent['login_time']
    })

@app.route('/session/messages/<session_id>')
def get_session_messages(session_id):
    if session_id not in sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    session = sessions[session_id]
    return jsonify({
        'session_id': session_id,
        'status': session.status,
        'messages': session.messages,
        'agent_id': session.agent_id
    })

@app.route('/admin/stats')
def admin_stats():
    with session_lock:
        active_sessions = len([s for s in sessions.values() if s.status in ['bot', 'waiting_agent', 'with_agent']])
        waiting_sessions = len([s for s in sessions.values() if s.status == 'waiting_agent'])
        agent_sessions = len([s for s in sessions.values() if s.status == 'with_agent'])
        
        queue_data = []
        for session_id in agent_queue:
            if session_id in sessions:
                session = sessions[session_id]
                wait_time = (datetime.now() - session.agent_requested_at).total_seconds() if session.agent_requested_at else 0
                last_message = session.messages[-1]['content'] if session.messages else None
                queue_data.append({
                    'session_id': session_id,
                    'wait_time': int(wait_time),
                    'last_message': last_message
                })
    
    return jsonify({
        'active_sessions': active_sessions,
        'queue_length': len(agent_queue),
        'waiting_sessions': waiting_sessions,
        'agent_sessions': agent_sessions,
        'active_agents': len(active_agents),
        'queue': queue_data
    })

# Enhanced route for customer interface
@app.route('/enhanced')
def enhanced_chatbot():
    return render_template('enhanced_chatbot.html')

# Agent dashboard route
@app.route('/agent')
def agent_dashboard():
    return render_template('agent_dashboard.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

