import os
# Install the ModelArk SDK via pip install byteplus-python-sdk-v2
from byteplussdkarkruntime import Ark

# Initialize the ModelArk client, reading your API Key from environment variables
client = Ark(
    api_key='yourapikey',
    )

# Create a chat request
response = client.chat.completions.create(
    # Replace <Model> with the Model ID of your model
    model="skylark-vision-250515",
    messages = [
        {
            # Specify the message role as user
            "role": "user",  
            "content": [   
                # Image information, the image hoping the model to understand
                {"type": "image_url", "image_url": {"url":  "your.jpgpath"}},
                # Text message, the question hoping the model to answer based on image information
                {"type": "text", "text": "describe this photok？"}, 
            ],
        }
    ],
)

print(response.choices[0].message.content)