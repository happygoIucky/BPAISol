      
import requests
import time

submit_task_url = 'https://openspeech.bytedance.com/api/v1/virtual_human/async/submit'
query_task_url = 'https://openspeech.bytedance.com/api/v1/virtual_human/async/query'

appid = 'xxx'
access_token = 'xxx'

def submit_task(role, audio_url, audio_format):
    text = '<speak><audio url="{}" format="{}"/></speak>'.format(audio_url, audio_format)
    data = {
        'appid': appid,
        'access_token': access_token,
        'avatar_type': '2d',
        'text': text,
        'role': role,
        'input_mode': 'audio',
        'codec': 'mp4'
    }
    response = requests.post(url=submit_task_url, json=data, timeout=10)
    print("get response status_code:{} resp:{}".format(response.status_code, response.text))
    if response.status_code != 200:
        raise Exception("submit task fail, http_code:{} http_resp:{}".format(response.status_code, response.text))
    else:
        resp = response.json()
        if resp['code'] != 0:
            raise Exception("submit task fail, code:{} message:{} logid:{}".format(resp['code'], resp['message'], resp['logid']))
        else:
            return resp['data']['task_id']

def query_task(task_id, timeout):
    start_time = time.time()
    sleep_interval = 15
    url = "{}?task_id={}".format(query_task_url, task_id)
    while True:
        if int(time.time()-start_time) >= timeout:
            raise Exception("task:{} timeout!".format(task_id))
        response = requests.get(url=url, timeout=2)
        print("query task, status_code:{} resp:{}".format(response.status_code, response.text))
        if response.status_code != 200:
            #对于偶现的请求失败，可以忽略
            time.sleep(sleep_interval)
            continue
        resp = response.json()
        if resp['code'] != 0:
            print("query task fail, task_id:{} code:{} message:{}".format(task_id, resp['code'], resp['message']))
            time.sleep(sleep_interval)
            continue
        task_status = resp['data']['task_status']
        if task_status == 0:
            time.sleep(sleep_interval)
            continue
        elif task_status == 2:
            failure_reason = resp['data']['failure_reason']
            raise Exception("task run fail, reason:{}".format(failure_reason))
        return resp['data']['video_url']
    
if __name__ == '__main__':
    role = 'xxx'
    audio_url = 'xxx'
    audio_format = 'xxx' # wav,mp3
    task_id = submit_task(role, audio_url, audio_format)
    timeout = 300
    video_url = query_task(task_id, timeout)
    print("generate video succ: {}".format(video_url))

    