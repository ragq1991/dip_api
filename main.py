from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import time
import progressbar
from pprint import pprint
import json
import os
import requests

class YaUpLoader:
    def __init__(self, token: str):
        self.token = 'OAuth ' + token
        self.url = 'https://cloud-api.yandex.net/v1/disk/'
        self.headers = {'Accept': 'application/json', 'Authorization': self.token}
        self.json = []

    def create_catalog(self, path: str):
        """Метод создает каталог"""
        url = self.url + 'resources'
        params = {'path': path}
        resp = requests.put(url, params=params, headers=self.headers)
        return resp.status_code

    def upload_vk_list(self, list_items):
        print('Upload photo from VK: ')
        bar = progressbar.progressbar(range(len(list_items)))
        for item, value in list_items.items():
            bar.__next__()
            time.sleep(1.02)
            self.upload('disk:/vk_photo/image' + str(item) + '_' + str(value['likes']) + '.jpg', value['url'],
                        value['height'], value['width'])

    def upload(self, path, file_url, height=0, witdh=0):
        """Метод загружает файлы по ссылкам"""
        url = self.url + 'resources/upload'
        params = {'path': path, 'url': file_url}
        resp = requests.post(url, params=params, headers=self.headers)
        pos = path.rfind('/')
        file_name = path[pos + 1:len(path)]
        self.json.append({'file_name': file_name, 'size': str(height) + 'x' + str(witdh)})
        return resp.status_code

    def upload_file(self, file_path: str):
        """Метод загружает файл с жесткого диска"""
        pos = file_path.rfind('\\')
        file_name = file_path[pos+1:len(file_path)]
        url = self.url + 'resources/upload'
        params = {'path': file_name, 'overwrite': 'true'}
        resp = requests.get(url, params=params, headers=self.headers).json()
        upload_url = resp['href']
        resp = requests.put(upload_url, data=open(file_path, 'rb'))
        return resp

    def save_info(self, path=os.path.abspath(os.getcwd())):
        with open(path + '\\' + 'info.json', 'w') as f:
            json.dump(self.json, f, ensure_ascii=False, indent=2)
        return path + '\\' + 'info.json'

class ApiVK:
    def __init__(self, client_id, client_secret, serv_key, grant_type, ver='5.130'):
        """Авторизация здесь"""
        self.url = 'https://oauth.vk.com/'
        self.ver = ver
        self.parameters = {'client_id': client_id,
                           'client_secret': client_secret,
                           'grant_type': grant_type,
                           'v': self.ver}
        url = self.url + 'access_token'
        self.resp = requests.get(url, params=self.parameters).json()
        self.token = self.resp['access_token']
        self.serv_key = serv_key

    def get_photo(self, owner_id, count=5):
        print('Getting photo from VK: ')
        bar = progressbar.progressbar(range(count))
        """Метод возвращает ссылки на фото + доп.информацию"""
        url = 'https://api.vk.com/method/photos.get'
        parameters = {'owner_id': owner_id, 'album_id': 'wall', 'extended': 1, 'photo_sizes': 0, 'count': count,
                      'access_token': self.serv_key, 'v': self.ver}
        resp = requests.get(url, params=parameters)
        if resp.status_code == 200:
            json_f = resp.json()
            i = 0
            photo = {}
            for item in json_f['response']['items']:
                bar.__next__()
                time.sleep(1.02)
                i += 1
                height = 0
                width = 0
                for size in item['sizes']:
                    if size['height'] * size['width'] > height * width:
                        height = size['height']
                        width = size['width']
                        url = size['url']
                photo[i] = {'id': item['id'], 'likes': item['likes']['count'], 'url': url, 'height': height,
                            'width': width}
            print()
            return photo.copy()

def __main__():
    vk = ApiVK('7805267', '3U35CT7r5H4M527IrA6S', 'c2e7f6b0c2e7f6b0c2e7f6b0d1c290efe3cc2e7c2e7f6b0a2b860923852733185e467d2',
           'client_credentials', '5.130')
    photo = vk.get_photo('646854180', 5)

    ya = YaUpLoader('AQAAAAARbtX1AADLWxAE9XnSmUgpuBeAiJxlZBI')
    ya.create_catalog('vk_photo')
    ya.upload_vk_list(photo)
    file_info = ya.save_info()
    ya.upload_file(file_info)
