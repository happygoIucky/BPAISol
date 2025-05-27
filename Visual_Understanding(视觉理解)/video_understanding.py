import os
# 通过 pip install volcengine-python-sdk[ark] 安装方舟SDK
from volcenginesdkarkruntime import Ark

# 替换 <MODEL> 为模型的Model ID
model="doubao-1.5-vision-pro"

# 初始化Ark客户端，从环境变量中读取您的API Key
client = Ark(
    api_key='yourapikey',
    )

# 创建一个对话请求
response = client.chat.completions.create(
    # 指定您部署了视觉理解大模型的推理接入点ID
    model = model,
    messages = [
        {
            # 指定消息的角色为用户
            "role": "user",  
            "content": [   
                {
                    "type": "video_url",
                    "video_url": {
                        # 您可以替换链接为您的实际视频链接
                        "url":  "yourvideopath",
                    }
                },
            ],
        }
    ],
)

print(response.choices[0].message.content)