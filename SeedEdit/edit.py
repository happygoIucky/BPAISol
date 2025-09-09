import os 
from byteplussdkarkruntime import Ark
 
# Make sure that you have stored the API Key in the environment variable ARK_API_KEY 
# Initialize the Ark client to read your API Key from an environment variable 
client = Ark( 
    # This is the default path. You can configure it based on the service location 
    base_url="https://ark.ap-southeast.bytepluses.com/api/v3", 
    # Get your Key authentication from the environment variable. This is the default mode and you can modify it as required 
 api_key= “Sdadasdasdadadadad"


imagesResponse = client.images.generate( 
        model="seededit-3-0-i2i-250628",
        prompt="Make the bubbles heart-shaped", 
        image="https://ark-doc.tos-ap-southeast-1.bytepluses.com/seededit_i2i.jpeg", 
        response_format="url", 
        size="adaptive", 
        seed=123, 
        guidance_scale=5.5, 
        watermark=True
)
 
print(imagesResponse.data[0].url)