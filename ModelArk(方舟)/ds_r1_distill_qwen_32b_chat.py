import os
from byteplussdkarkruntime import Ark
# Get API Key
client = Ark(api_key='ypurapikey')
completion = client.chat.completions.create(
    # Replace <MODEL> with Model ID / your inference endpoint ID 
    model="deepseek-r1-distill-qwen-32b-250120",
    messages=[
        {"role": "user", "content": "hello, can you tell me what does bytedance do in only 2 sentences?"}
    ]
)
print(completion.choices[0].message)