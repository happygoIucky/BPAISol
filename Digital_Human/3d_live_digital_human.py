#import bytedlogger
import json
import logging
import traceback
import uuid
import websocket

#bytedlogger.config_default()

# client side
StartLiveHeader = "|CTL|00|"
CloseLiveHeader = "|CTL|01|"
EndStreamingAudioHeader = "|CTL|12|"
StreamingAudioHeader = "|DAT|02|"

# server side
StartLiveAckHeader = "|MSG|00|"
PlayStatusHeader = "|DAT|02|"

PlayStatusVoiceStart = "voice_start"
PlayStatusVoiceEnd = "voice_end"

pkgSize = 16000 * 2  # 1s PCM data (16kHz, 1 channel, 16 bits)


def init() -> websocket.WebSocket:
    # 开播
    ws = websocket.create_connection("wss://openspeech.bytedance.com/virtual_human/avatar_live/live")
    startLiveInfo = {
        "live": {
            "live_id": "xxxx",  # 填写
        },
        "auth": {
            "appid": "xxx",  # 填写
            "token": "xxx",  # 填写
        },
        "avatar": {
            "avatar_type": "3min",
            "input_mode": "audio",
            "role": "xxx",  # 填写
        },
        "streaming": {  # 填写
            "type": "rtmp",
           # "rtmp_addr": "rtmps://push-rtmp-l11-act.hypstarcdn.com/rtmlive/stream-2423539180971754578?c=unknown&expire=1755105641&l_region=Singapore-Central&sign=e5febc9e7ade1a7bd6428709e04f7bad&th_region=sg",          
            "rtmp_addr": "rtmp:/xxxx",
        },
    }
    logging.info(startLiveInfo)
    ws.send(StartLiveHeader + json.dumps(startLiveInfo))
    # TODO：预计 10s 内，需要加超时
    ack = ws.recv()
    logging.info(ack)
    ackInfo = json.loads(ack[8:])
    if ackInfo["code"] != 1000:
        raise Exception(f"[{ackInfo['code']}] {ackInfo['message']}")
    return ws


def sendAudio(ws: websocket.WebSocket, filePath: str):
    # 发送流式音频
    with open(filePath, "rb") as f:
        audio = f.read()
    start = 0
    while start < len(audio):
        end = start + pkgSize
        if end > len(audio):
            end = len(audio)
        ws.send(StreamingAudioHeader.encode() + audio[start:end], websocket.ABNF.OPCODE_BINARY)
        start = end
    ws.send(EndStreamingAudioHeader)
    voiceStart = False
    while True:
        playStatus = ws.recv()
        logging.info(playStatus)
        if str(playStatus[:8]) == PlayStatusHeader:
            playStatusInfo = json.loads(playStatus[8:])
            if not voiceStart:
                # TODO：先等待 voice_start，预计 500ms 左右，需要加超时
                if playStatusInfo["type"] != PlayStatusVoiceStart:
                    raise Exception(f"play status type should by voice_start but {playStatusInfo['type']}")
                else:
                    voiceStart = True
            else:
                # TODO：再等待 voice_end，预计音频长度+500ms 左右，需要加超时
                if playStatusInfo["type"] != PlayStatusVoiceEnd:
                    raise Exception(f"play status type should by voice_end but {playStatusInfo['type']}")
                else:
                    return


def close(ws: websocket.WebSocket):
    # 关播
    ws.send(CloseLiveHeader)


if __name__ == "__main__":
    try:
        ws = init()
        sendAudio(ws, "xxx.pcm")
        close(ws)
    except Exception as e:
        logging.error(e)
        logging.error(traceback.format_exc())