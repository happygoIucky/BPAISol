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

    b. once done, save the file and run "ngrok start --all" and you shall see the below (check your own url)
        e/g. Forwarding   https://abcd.ngrok-free.app -> http://localhost:3000                                                   
             Forwarding   https://efgh.ngrok-free.app -> http://localhost:3001  

5. once done, go to 
    a. Server folder and run "yarn dev"
    b. Root folder run "yarn dev:flexible"



< RAG Cloud API TUTORIAL >

1. Please ensure your BP ID is whitelisted before proceeding
2. git clone https://github.com/happygoIucky/BPAISol/tree/main/RAG_API_Cloud
3. Follow the step 
    a. step1_rag_auth_n_create_kb.py - create KB 
    b. step2_rag_verify_kb.py - Verify KB
    c. step3_rag_add_doc.py - Upload any Docs
    d. step4_rag_search_knowledge_ask_docu.py - Query KB Only
    e. step6_rag_chatbot-with-ai.py - Chatbot interface with KB
    f. RAG_API_Cloud/templates/index-ai.html - rename to index.html
4. once 3 is done, "python step6_rag_chatbot-with-ai.py"


