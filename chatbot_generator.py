#!/usr/bin/env python3
"""
Advanced Chatbot Generator
Creates a modern, feature-rich chatbot with multiple AI provider support
"""

import os
import json
from flask import Flask, request, render_template, jsonify, session
import requests
from datetime import datetime
import uuid
import logging
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatbotGenerator:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = str(uuid.uuid4())
        self.conversation_history = {}
        self.setup_routes()
        
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            return render_template('chatbot.html')
            
        @self.app.route('/api/chat', methods=['POST'])
        def chat():
            try:
                data = request.get_json()
                user_message = data.get('message', '').strip()
                chat_mode = data.get('mode', 'simple')  # simple, rag, voice
                
                if not user_message:
                    return jsonify({'error': 'Message cannot be empty'}), 400
                    
                # Get or create session ID
                session_id = session.get('session_id', str(uuid.uuid4()))
                session['session_id'] = session_id
                
                # Initialize conversation history for new sessions
                if session_id not in self.conversation_history:
                    self.conversation_history[session_id] = []
                    
                # Process message based on mode
                if chat_mode == 'rag':
                    response = self.handle_rag_chat(user_message, session_id)
                elif chat_mode == 'voice':
                    response = self.handle_voice_chat(user_message, session_id)
                else:
                    response = self.handle_simple_chat(user_message, session_id)
                    
                # Store conversation
                self.conversation_history[session_id].append({
                    'user': user_message,
                    'assistant': response,
                    'timestamp': datetime.now().isoformat(),
                    'mode': chat_mode
                })
                
                return jsonify({
                    'response': response,
                    'session_id': session_id,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Chat error: {str(e)}")
                return jsonify({'error': 'Internal server error'}), 500
                
        @self.app.route('/api/history/<session_id>')
        def get_history(session_id):
            """Get conversation history for a session"""
            history = self.conversation_history.get(session_id, [])
            return jsonify({'history': history})
            
        @self.app.route('/api/clear', methods=['POST'])
        def clear_history():
            """Clear conversation history"""
            session_id = session.get('session_id')
            if session_id and session_id in self.conversation_history:
                self.conversation_history[session_id] = []
            return jsonify({'status': 'cleared'})
            
    def handle_simple_chat(self, message: str, session_id: str) -> str:
        """Handle simple chat without external APIs"""
        # Simple rule-based responses for demo
        message_lower = message.lower()
        
        if 'hello' in message_lower or 'hi' in message_lower:
            return "Hello! I'm your AI assistant. How can I help you today?"
        elif 'how are you' in message_lower:
            return "I'm doing great! Thanks for asking. How can I assist you?"
        elif 'what can you do' in message_lower:
            return "I can help you with various tasks including answering questions, providing information, and having conversations. What would you like to know?"
        elif 'bye' in message_lower or 'goodbye' in message_lower:
            return "Goodbye! Feel free to come back anytime if you need help."
        else:
            return f"I understand you said: '{message}'. This is a demo chatbot. In a real implementation, this would connect to an AI service like OpenAI, Claude, or a local LLM."
            
    def handle_rag_chat(self, message: str, session_id: str) -> str:
        """Handle RAG-enhanced chat (placeholder for real implementation)"""
        # This would integrate with your existing RAG system
        return f"[RAG Mode] Processing your query: '{message}'. This would search the knowledge base and provide contextual answers."
        
    def handle_voice_chat(self, message: str, session_id: str) -> str:
        """Handle voice-enabled chat (placeholder for real implementation)"""
        # This would integrate with ASR/TTS services
        return f"[Voice Mode] Voice response for: '{message}'. This would include speech-to-text and text-to-speech capabilities."
        
    def create_html_template(self):
        """Create the HTML template for the chatbot"""
        html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advanced AI Chatbot</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .chat-container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            width: 100%;
            max-width: 800px;
            height: 600px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .chat-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
            position: relative;
        }
        
        .chat-header h1 {
            font-size: 24px;
            margin-bottom: 10px;
        }
        
        .mode-selector {
            display: flex;
            gap: 10px;
            justify-content: center;
            margin-top: 10px;
        }
        
        .mode-btn {
            padding: 5px 15px;
            border: 1px solid rgba(255,255,255,0.3);
            background: rgba(255,255,255,0.1);
            color: white;
            border-radius: 15px;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 12px;
        }
        
        .mode-btn.active {
            background: rgba(255,255,255,0.3);
            border-color: rgba(255,255,255,0.5);
        }
        
        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #f8f9fa;
        }
        
        .message {
            margin-bottom: 15px;
            display: flex;
            align-items: flex-start;
            gap: 10px;
        }
        
        .message.user {
            flex-direction: row-reverse;
        }
        
        .message-content {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 18px;
            word-wrap: break-word;
        }
        
        .message.user .message-content {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .message.assistant .message-content {
            background: white;
            border: 1px solid #e0e0e0;
            color: #333;
        }
        
        .avatar {
            width: 35px;
            height: 35px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            flex-shrink: 0;
        }
        
        .avatar.user {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .avatar.assistant {
            background: #f0f0f0;
            color: #666;
        }
        
        .chat-input {
            padding: 20px;
            background: white;
            border-top: 1px solid #e0e0e0;
        }
        
        .input-container {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .message-input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #ddd;
            border-radius: 25px;
            outline: none;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        
        .message-input:focus {
            border-color: #667eea;
        }
        
        .send-btn {
            padding: 12px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            transition: transform 0.2s;
            font-size: 14px;
        }
        
        .send-btn:hover {
            transform: translateY(-2px);
        }
        
        .send-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .clear-btn {
            padding: 8px 16px;
            background: #ff6b6b;
            color: white;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            font-size: 12px;
            transition: background 0.3s;
        }
        
        .clear-btn:hover {
            background: #ff5252;
        }
        
        .typing-indicator {
            display: none;
            padding: 10px;
            font-style: italic;
            color: #666;
        }
        
        .typing-dots {
            display: inline-block;
            animation: typing 1.4s infinite;
        }
        
        @keyframes typing {
            0%, 60%, 100% { opacity: 0; }
            30% { opacity: 1; }
        }
        
        .status-bar {
            padding: 10px 20px;
            background: #f8f9fa;
            border-top: 1px solid #e0e0e0;
            font-size: 12px;
            color: #666;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>🤖 Advanced AI Chatbot</h1>
            <p>Powered by Multiple AI Providers</p>
            <div class="mode-selector">
                <div class="mode-btn active" data-mode="simple">💬 Simple</div>
                <div class="mode-btn" data-mode="rag">📚 RAG</div>
                <div class="mode-btn" data-mode="voice">🎤 Voice</div>
            </div>
        </div>
        
        <div class="chat-messages" id="chatMessages">
            <div class="message assistant">
                <div class="avatar assistant">🤖</div>
                <div class="message-content">
                    Hello! I'm your AI assistant. I can help you in different modes:
                    <br>• <strong>Simple:</strong> Basic conversation
                    <br>• <strong>RAG:</strong> Knowledge-base enhanced responses
                    <br>• <strong>Voice:</strong> Speech-enabled interaction
                    <br><br>How can I help you today?
                </div>
            </div>
        </div>
        
        <div class="typing-indicator" id="typingIndicator">
            <div class="avatar assistant">🤖</div>
            <div class="message-content">
                AI is thinking<span class="typing-dots">...</span>
            </div>
        </div>
        
        <div class="chat-input">
            <div class="input-container">
                <input type="text" class="message-input" id="messageInput" 
                       placeholder="Type your message here..." maxlength="1000">
                <button class="send-btn" id="sendBtn">Send</button>
                <button class="clear-btn" id="clearBtn">Clear</button>
            </div>
        </div>
        
        <div class="status-bar">
            <span id="statusText">Ready</span>
            <span id="modeText">Mode: Simple</span>
        </div>
    </div>
    
    <script>
        class Chatbot {
            constructor() {
                this.currentMode = 'simple';
                this.isTyping = false;
                this.initializeElements();
                this.bindEvents();
            }
            
            initializeElements() {
                this.chatMessages = document.getElementById('chatMessages');
                this.messageInput = document.getElementById('messageInput');
                this.sendBtn = document.getElementById('sendBtn');
                this.clearBtn = document.getElementById('clearBtn');
                this.typingIndicator = document.getElementById('typingIndicator');
                this.statusText = document.getElementById('statusText');
                this.modeText = document.getElementById('modeText');
                this.modeButtons = document.querySelectorAll('.mode-btn');
            }
            
            bindEvents() {
                this.sendBtn.addEventListener('click', () => this.sendMessage());
                this.clearBtn.addEventListener('click', () => this.clearChat());
                this.messageInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        this.sendMessage();
                    }
                });
                
                this.modeButtons.forEach(btn => {
                    btn.addEventListener('click', () => this.switchMode(btn.dataset.mode));
                });
            }
            
            switchMode(mode) {
                this.currentMode = mode;
                this.modeButtons.forEach(btn => btn.classList.remove('active'));
                document.querySelector(`[data-mode="${mode}"]`).classList.add('active');
                this.modeText.textContent = `Mode: ${mode.charAt(0).toUpperCase() + mode.slice(1)}`;
                this.statusText.textContent = `Switched to ${mode} mode`;
            }
            
            async sendMessage() {
                const message = this.messageInput.value.trim();
                if (!message || this.isTyping) return;
                
                this.addMessage(message, 'user');
                this.messageInput.value = '';
                this.showTyping();
                
                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            message: message,
                            mode: this.currentMode
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        this.addMessage(data.response, 'assistant');
                        this.statusText.textContent = 'Message sent successfully';
                    } else {
                        this.addMessage('Sorry, there was an error processing your request.', 'assistant');
                        this.statusText.textContent = 'Error: ' + (data.error || 'Unknown error');
                    }
                } catch (error) {
                    this.addMessage('Sorry, I\'m having trouble connecting. Please try again.', 'assistant');
                    this.statusText.textContent = 'Connection error';
                } finally {
                    this.hideTyping();
                }
            }
            
            addMessage(content, sender) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${sender}`;
                
                const avatar = document.createElement('div');
                avatar.className = `avatar ${sender}`;
                avatar.textContent = sender === 'user' ? '👤' : '🤖';
                
                const messageContent = document.createElement('div');
                messageContent.className = 'message-content';
                messageContent.textContent = content;
                
                messageDiv.appendChild(avatar);
                messageDiv.appendChild(messageContent);
                
                this.chatMessages.appendChild(messageDiv);
                this.scrollToBottom();
            }
            
            showTyping() {
                this.isTyping = true;
                this.typingIndicator.style.display = 'flex';
                this.sendBtn.disabled = true;
                this.scrollToBottom();
            }
            
            hideTyping() {
                this.isTyping = false;
                this.typingIndicator.style.display = 'none';
                this.sendBtn.disabled = false;
            }
            
            scrollToBottom() {
                this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
            }
            
            async clearChat() {
                if (confirm('Are you sure you want to clear the chat history?')) {
                    try {
                        await fetch('/api/clear', { method: 'POST' });
                        this.chatMessages.innerHTML = `
                            <div class="message assistant">
                                <div class="avatar assistant">🤖</div>
                                <div class="message-content">
                                    Chat history cleared. How can I help you today?
                                </div>
                            </div>
                        `;
                        this.statusText.textContent = 'Chat cleared';
                    } catch (error) {
                        this.statusText.textContent = 'Error clearing chat';
                    }
                }
            }
        }
        
        // Initialize chatbot when page loads
        document.addEventListener('DOMContentLoaded', () => {
            new Chatbot();
        });
    </script>
</body>
</html>
        '''
        
        # Create templates directory if it doesn't exist
        templates_dir = 'templates'
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir)
            
        # Write the HTML template
        with open(os.path.join(templates_dir, 'chatbot.html'), 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        logger.info("HTML template created successfully")
        
    def run(self, host='0.0.0.0', port=5000, debug=True):
        """Run the chatbot server"""
        self.create_html_template()
        logger.info(f"Starting chatbot server on http://{host}:{port}")
        logger.info("Features available:")
        logger.info("  • Modern responsive UI")
        logger.info("  • Multiple chat modes (Simple, RAG, Voice)")
        logger.info("  • Session management")
        logger.info("  • Conversation history")
        logger.info("  • Real-time typing indicators")
        
        self.app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    # Create and run the chatbot
    chatbot = ChatbotGenerator()
    chatbot.run()