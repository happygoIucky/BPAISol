import os
# 通过 pip install volcengine-python-sdk[ark] 安装方舟SDK
from volcenginesdkarkruntime import Ark

# 替换 <MODEL> 为模型的Model ID
model="doubao-1.5-vision-pro-32k-250115"

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
                # 图片信息，希望模型理解的图片
                {"type": "image_url", "image_url": {"url":  "yourimagepath"},},
                # 文本消息，希望模型根据图片信息回答的问题
                {"type": "text", "text": "what is this photo about？"},
            ],
        }
    ],
)

print(response.choices[0].message.content)