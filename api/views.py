import os
from io import BytesIO
import json
from requests import post
from django.http import HttpResponse
from pydub import AudioSegment, playback
from .secret_config import kakao_rest_api_key
from mysite.settings import MEDIA_ROOT
from .models import AlertTbl, Shop


class KakaoSound:
    def __init__(self):
        self.kakao_recognize_url = "https://kakaoi-newtone-openapi.kakao.com/v1/recognize"
        self.kakao_synthesize_url = "https://kakaoi-newtone-openapi.kakao.com/v1/synthesize"
        self.headers = {
            "Authorization": "KakaoAK " + kakao_rest_api_key,
        }

    def recognize(self, audio_data):
        headers = {
            "Content-Type": "application/octet-stream",
            "X-DSS-Service": "DICTATION",
            **self.headers,
        }
        try:
            res = post(self.kakao_recognize_url, \
                    headers=headers, data=audio_data)
            result_json_string = res.text[ # 슬라이싱
                res.text.index('{"type":"finalResult"') : \
                res.text.rindex('}') + 1
            ]
            result = json.loads(result_json_string)
            value = result['value']
            print(f"\n음성 인식 결과> {value}")
        except:
            value = None
            print("음성 인식 실패")
        return value

    def synthesize(self, msg):
        headers = {
            "Content-Type" : "application/xml",
            **self.headers,
        }
        data = f"""
        <speak>{msg}</speak>
        """.encode('utf-8')

        res = post(self.kakao_synthesize_url, headers=headers, data=data)
        if (res.status_code != 200):
            print(res, res.text)
        else:
            sound = BytesIO(res.content)
            song = AudioSegment.from_mp3(sound)
            playback.play(song)

shop = Shop.objects.get(id=9)

# 싱글톤 적용할 것
def play_alert(request):
    sound = AudioSegment.from_mp3(os.path.join(MEDIA_ROOT,'audio/alert.mp3'))
    playback.play(sound)
    alert = AlertTbl(shop=shop, alert_msg='alert_audio')
    alert.save()
    return HttpResponse('<h1>Alerted</h1>')

kakao = KakaoSound()

# 요청 메시지를 카카오 음성 합성해서 재생
def play_announce(request):
    msg = request.GET.get('message', None)
    kakao.synthesize(msg)
    alert = AlertTbl(shop=shop, alert_msg=msg)
    alert.save()
    return HttpResponse('<h1>Announced</h1>')
