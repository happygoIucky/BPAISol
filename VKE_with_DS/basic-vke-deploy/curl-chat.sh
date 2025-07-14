# you can use this for both vllm or sglang test

curl http://your-node-ip:your-node-port/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
        "model": "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
        "messages": [
          {"role": "user", "content": "What is the capital of Japan?"}
        ],
        "temperature": 0.7,
        "max_tokens": 256
      }'