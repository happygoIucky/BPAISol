import requests

url = "https://vlm.byteplus-demo.com/api/v1/vlm/process"

headers = {
    "accept": "application/json",
    "Content-Type": "application/json"
}

data = {
  "url_link": "yourpdfpath",
  "prompt": "OCR",
  "base_url": "https://ark.ap-southeast.bytepluses.com/api/v3",
  "model_name": "yourvisionep",
  "api_key": "yourapikey"

}

response = requests.post(url, headers=headers, json=data)

print("Status Code:", response.status_code)
print("Response:", response.json())