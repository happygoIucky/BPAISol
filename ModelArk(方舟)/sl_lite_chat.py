import os
from byteplussdkarkruntime import Ark
# Get API Key
client = Ark(api_key='yourpaikey')
completion = client.chat.completions.create(
    # Replace <MODEL> with Model ID / your inference endpoint ID 
    model="skylark-lite-250215",
    messages=[
        {"role": "user", "content": "hello, can you tell me what does bytedance do in only 2 sentences?"}
    ]
)
print(completion.choices[0].message)