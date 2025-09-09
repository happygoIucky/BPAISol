# 🤖 Advanced AI Chatbot Generator

A modern, feature-rich chatbot application with multiple AI provider support, built with Flask and vanilla JavaScript.

## ✨ Features

### 🎨 Modern UI/UX
- **Responsive Design**: Works perfectly on desktop and mobile devices
- **Beautiful Gradient Theme**: Eye-catching purple gradient design
- **Real-time Typing Indicators**: Shows when AI is thinking
- **Smooth Animations**: Polished user experience with CSS transitions
- **Message Avatars**: Visual distinction between user and AI messages

### 🧠 Multiple Chat Modes
1. **Simple Mode** 💬: Basic conversational AI with rule-based responses
2. **RAG Mode** 📚: Knowledge-base enhanced responses (ready for integration)
3. **Voice Mode** 🎤: Speech-enabled interaction (ready for integration)

### 🔧 Technical Features
- **Session Management**: Maintains conversation context
- **Conversation History**: Stores and retrieves chat history
- **Error Handling**: Graceful error management
- **RESTful API**: Clean API endpoints for chat functionality
- **Modular Architecture**: Easy to extend and customize

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd /Users/bytedance/Desktop/BPAISol
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the chatbot**:
   ```bash
   python chatbot_generator.py
   ```

4. **Open your browser** and go to:
   ```
   http://localhost:5000
   ```

## 📁 Project Structure

```
BPAISol/
├── chatbot_generator.py      # Main chatbot application
├── requirements.txt          # Python dependencies
├── README_Chatbot.md        # This documentation
└── templates/               # Auto-generated HTML templates
    └── chatbot.html        # Main chatbot interface
```

## 🔌 API Endpoints

### Chat Endpoint
```http
POST /api/chat
Content-Type: application/json

{
  "message": "Hello, how are you?",
  "mode": "simple"  // "simple", "rag", or "voice"
}
```

**Response:**
```json
{
  "response": "Hello! I'm doing great. How can I help you?",
  "session_id": "uuid-string",
  "timestamp": "2024-01-01T12:00:00"
}
```

### History Endpoint
```http
GET /api/history/<session_id>
```

### Clear History
```http
POST /api/clear
```

## 🛠 Customization

### Adding AI Provider Integration

To integrate with real AI services, modify the handler methods in `chatbot_generator.py`:

#### OpenAI Integration Example:
```python
def handle_simple_chat(self, message: str, session_id: str) -> str:
    import openai
    
    openai.api_key = "your-api-key"
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message}
        ]
    )
    
    return response.choices[0].message.content
```

#### RAG Integration Example:
```python
def handle_rag_chat(self, message: str, session_id: str) -> str:
    # Search knowledge base
    context = self.search_knowledge_base(message)
    
    # Combine with AI response
    prompt = f"Context: {context}\n\nQuestion: {message}"
    return self.call_ai_service(prompt)
```

### Customizing the UI

The HTML template is auto-generated in the `templates/` directory. You can:

1. **Modify colors**: Change the CSS gradient values
2. **Add new modes**: Update both Python handlers and JavaScript
3. **Customize avatars**: Change emoji or add image avatars
4. **Add features**: Implement file upload, voice recording, etc.

### Environment Configuration

Create a `.env` file for sensitive configuration:
```env
# AI Service Configuration
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Database Configuration
DATABASE_URL=sqlite:///chatbot.db

# App Configuration
SECRET_KEY=your_secret_key
DEBUG=True
```

## 🔗 Integration with Existing Services

This chatbot can be easily integrated with your existing AI services:

### BytePlus/Volcengine Integration
```python
# Use your existing volcengine auth code
from volcengine.auth.SignerV4 import SignerV4
# ... integrate with existing BP services
```

### Voice Integration
```python
# Integrate with your existing ASR/TTS services
# Use the voice chat implementations from your Conversation_AI folder
```

### RAG Integration
```python
# Use your existing RAG implementation
# Import from RAG_API_Cloud folder
```

## 🚀 Deployment

### Local Development
```bash
python chatbot_generator.py
```

### Production Deployment

#### Using Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 chatbot_generator:app
```

#### Using Docker:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "chatbot_generator.py"]
```

## 🧪 Testing

### Manual Testing
1. Start the server
2. Open browser to `http://localhost:5000`
3. Test different chat modes
4. Verify conversation history
5. Test error handling

### API Testing with curl
```bash
# Test chat endpoint
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "mode": "simple"}'

# Test clear endpoint
curl -X POST http://localhost:5000/api/clear
```

## 🔧 Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   # Change port in chatbot_generator.py or kill existing process
   lsof -ti:5000 | xargs kill -9
   ```

2. **Module not found**:
   ```bash
   # Ensure all dependencies are installed
   pip install -r requirements.txt
   ```

3. **Template not found**:
   ```bash
   # The app auto-creates templates, ensure write permissions
   chmod 755 .
   ```

### Debug Mode
The app runs in debug mode by default. To disable:
```python
chatbot.run(debug=False)
```

## 📈 Performance Optimization

### For High Traffic
1. **Use Redis for session storage**
2. **Implement connection pooling**
3. **Add caching for AI responses**
4. **Use async/await for AI API calls**

### Memory Management
```python
# Limit conversation history
MAX_HISTORY_LENGTH = 50

# Clean old sessions periodically
def cleanup_old_sessions():
    # Implementation here
    pass
```

## 🤝 Contributing

1. Fork the project
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

For questions or issues:
1. Check the troubleshooting section
2. Review the existing code examples
3. Test with the provided API endpoints

---

**Happy Chatting! 🎉**

This chatbot generator provides a solid foundation for building sophisticated AI-powered conversational interfaces. Customize it to fit your specific needs and integrate with your preferred AI services.