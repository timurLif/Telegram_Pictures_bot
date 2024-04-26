import json
import time
import base64
import requests


class Text2ImageAPI:

    def __init__(self, url, api_key, secret_key):
        self.URL = url
        self.AUTH_HEADERS = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }

    def get_model(self):
        response = requests.get(self.URL + 'key/api/v1/models', headers=self.AUTH_HEADERS)
        data = response.json()
        return data[0]['id']

    def generate(self, prompt, model, images=1, width=1024, height=1024, style=3):
        styles = ["KANDINSKY", "UHD", "ANIME", "DEFAULT"]
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "style": styles[style],
            "generateParams": {
                "query": f"{prompt}"
            }
        }

        data = {
            'model_id': (None, model),
            'params': (None, json.dumps(params), 'application/json')
        }
        response = requests.post(self.URL + 'key/api/v1/text2image/run', headers=self.AUTH_HEADERS, files=data)
        data = response.json()
        return data['uuid']

    def check_generation(self, request_id, attempts=10, delay=10):
        while attempts > 0:
            response = requests.get(self.URL + 'key/api/v1/text2image/status/' + request_id, headers=self.AUTH_HEADERS)
            data = response.json()
            if data['status'] == 'DONE':
                return data['images']

            attempts -= 1
            time.sleep(delay)

def gen_pic(text, st=3, wh=1024, ht=1024):
    api = Text2ImageAPI('https://api-key.fusionbrain.ai/', '6DF927395FE982348BE61428D84DC415', '12F8381921643EEC029F6E94629A6A4C')
    model_id = api.get_model()
    uuid = api.generate(text, model_id, style=st, width=wh, height=ht)
    images = api.check_generation(uuid)
    # Здесь image_base64 - это строка с данными изображения в формате base64
    image_base64 = images[0] # Вставьте вашу строку base64 сюда
    # Декодируем строку base64 в бинарные данные
    image_data = base64.b64decode(image_base64)
    
    return image_data
