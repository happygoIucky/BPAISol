from flask import Flask, request, Response, stream_with_context
import requests
import json

app = Flask(__name__)

# === Your BytePlus Config ===
BYTEPLUS_ENDPOINT = "https://hiagent-byteplus.volcenginepaas.com/api/proxy/api/v1/chat_query"
API_KEY = ""
APP_KEY = ""
CONVERSATION_ID = ""  # Should be unique per user/session if possible
USER_ID = "" # random

@app.route("/chat/stream", methods=["POST"])
def chat_stream():
    data = request.get_json(silent=True)
    print("📥 Incoming JSON:", data)

    user_query = ""

    if data:
        if "messages" in data:
            messages = data.get("messages", [])
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    user_query = msg.get("content", "")
                    break
        else:
            user_query = data.get("query", "")

    if not user_query.strip():
        return Response("data: {\"error\": \"Empty query\"}\n\ndata: [DONE]\n\n", content_type="text/event-stream")

    def event_stream():
        print("🚀 Forwarding query to BytePlus...")
        headers = {
            "Apikey": API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "AppKey": APP_KEY,
            "Query": user_query,
            "AppConversationID": CONVERSATION_ID,
            "UserID": USER_ID,
            "ResponseMode": "blocking"  # Required for streaming response
        }

        try:
            with requests.post(BYTEPLUS_ENDPOINT, headers=headers, json=payload, stream=True) as r:
                for line in r.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    print("📡 Line from BytePlus:", line)
                    yield f"data: {line}\n\n"
                yield "data: [DONE]\n\n"
        except Exception as e:
            print("❌ Error while proxying:", e)
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\ndata: [DONE]\n\n"

    return Response(stream_with_context(event_stream()), content_type="text/event-stream")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)