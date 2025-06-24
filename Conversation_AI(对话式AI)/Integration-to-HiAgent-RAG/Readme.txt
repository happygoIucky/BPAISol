< CONVERSATIONAL AI TUTORIAL >

1. git clone https://github.com/byteplus-sdk/RTC_AIGC_Demo
2. Replace a few files as there's some changes to code in existing downloaded folder.
  Files to replace and change the field accordingly
  - RTC_AIGC_Demo/Server/sensitive.js
  - RTC_AIGC_Demo/src/config/voiceChat/llm.ts
     a. NOTE
        - if you are using thirdparty e.g. RAG, you must ensure the URL must be HTTPS ()
        - you can use ngrok to generate the free secure domain to your linux server
  - RTC_AIGC_Demo/src/config/index.ts
     a. NOTE
        - change to below URL to your domain instead of localhost 
        - e.g. export const getEnvDomain = () => 'https://xxxx.com';
        - you can use ngrok to generate the free secure domain to your linux server
3. If you run into formatting issue, just use "npx prettier --write <path>"

4. Guide to Setup NGROK for HTTPS/Secure access (Recommended for POC as it's easiest)
    a. After installing ngrok, you can edit the ngrok yaml file located at /root/.config/ngrok/ngrok.yaml
        version: "3"
        agent:
            authtoken: yourngroktoken - check online to generate this
        tunnels:
            web:
            addr: 3000 #this is for frontend
            proto: http
            db:
            addr: 3001 #this is for backend
            proto: http
            hi-agent:
            addr: 5000 #this is proxy to hi-agent backend service api
            proto: http

    b. once done, save the file and run "ngrok start --all" and you shall see the below (check your own url)
        e/g. Forwarding   https://abcd.ngrok-free.app -> http://localhost:3000                                                   
             Forwarding   https://efgh.ngrok-free.app -> http://localhost:3001  

5. once done, go to 
    a. Server folder and run "yarn dev"
    b. Root folder run "yarn dev:flexible"



< HiAgent RAG Integration TUTORIAL >

1. Go to HiAgent Console
2. Create KB, upload Docs
3. publish it and test the web service
4. Create API key for backend service API

# You can try below on curl or postman 
# The userID can be random, is more for audit purpose. typically will accountID of hiagent (can be found at account center)
#create conversation
curl --location 'https://hiagent-byteplus.volcenginepaas.com/api/proxy/api/v1/create_conversation' \--header 'Apikey: yourangetbackendseviceapikey' \--header 'Content-Type: application/json' \--data '{"AppKey": "yourangetbackendseviceapiappid", "UserID": "321"}'

#list conversation to see the AppConversationID
curl --location 'https://hiagent-byteplus.volcenginepaas.com/api/proxy/api/v1/get_conversation_list' \--header 'Apikey: yourangetbackendseviceapikey' \--header 'Content-Type: application/json' \--data '{"AppKey": "yourangetbackendseviceapiappid", "UserID": "321"}'

# create a chat with the corresponding AppConversationID
curl --location 'https://hiagent-byteplus.volcenginepaas.com/api/proxy/api/v1/chat_query' \--header 'Apikey: yourangetbackendseviceapikey' \--header 'Content-Type: application/json' \--data '{"AppKey": "yourangetbackendseviceappkey","Query":"tell me what is this pdf about","AppConversationID": "youruniqueappid","UserID": "321"}'


RAG Proxy Server
- python hi-agent-sse.py