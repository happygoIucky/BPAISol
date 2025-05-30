import os
# install pip install volcengine-python-sdk[ark]
from volcenginesdkarkruntime import Ark

# replace <MODEL> with the model ID
model="doubao-1.5-vision-pro"

# key in your api key or you could also put in your env variable
client = Ark(
    api_key='yourapikey',
    )

# Create a new chat
response = client.chat.completions.create(
    
    model = model,
    messages = [
        {
            "role": "user",  
            "content": [   
                {
                    "type": "video_url",
                    "video_url": {
                        # replace your video location below
                        "url":  "yourvideopath",
                    }
                },
            ],
        }
    ],
)

print(response.choices[0].message.content)