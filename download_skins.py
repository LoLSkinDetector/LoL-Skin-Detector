# -*- coding: utf-8 -*-

import urllib.request
import json
import re

from PyQt5 import QtCore


class DownloadSkins:
    DDRAGON_VERSIONS_URL = "https://ddragon.leagueoflegends.com/api/versions.json"
    
    def __init__(self):
        self.data_url = self.__champion_full_url()
        self.loading_images_url = "http://stelar7.no/cdragon/latest/loading-screen/"
        self.data = self.json_data()
        self.skin_urls = self.fetch_loading_skin_urls() 
        
    def json_data(self):
        with urllib.request.urlopen(self.data_url) as url:
            data = json.loads(url.read().decode())
            data = data['data']
            champion_skins_dict = {}
            for key, value in data.items():
                skin_numbers_names = {}
                for skin in value['skins']:
                    skin_numbers_names[skin['num']] = skin['name']
                champion_skins_dict.setdefault(value['key'], {}).update({'data': skin_numbers_names, 'name': key})
        return champion_skins_dict
    
    def __champion_full_url(self):
        return "http://ddragon.leagueoflegends.com/cdn/{}/data/en_US/championFull.json".format(self.__last_ddragon_version())
    
    def __last_ddragon_version(self):
        with urllib.request.urlopen(self.DDRAGON_VERSIONS_URL) as url:
            versions_json = json.loads(url.read().decode())
            return versions_json[0]
    
    def fetch_loading_skin_urls(self):
        skin_urls = []
        for champion_key, champion_data in self.data.items():
            for skin_id, skin_name in champion_data['data'].items():
                if skin_id == 0:
                    continue
                else:
                    skin_urls.append("{}/{}/{}.png".format(self.loading_images_url, champion_key, skin_id))
                   
        return skin_urls
                    
class DownloadThread(QtCore.QThread):
    data_downloaded = QtCore.pyqtSignal(object)

    def __init__(self, urls, dirpath):
        QtCore.QThread.__init__(self)
        self.urls = urls
        self.dirpath = dirpath

    def run(self):
        for url in self.urls:
            m = re.match(r".*\/\/(?P<champ_key>\d+)\/(?P<skin_num>\d+)\.(?P<file_ext>\w+)", url)
            filename = "{}_{}.{}".format(m['champ_key'], m['skin_num'], m['file_ext'])
            print("{}\{}".format(self.dirpath, filename))
            urllib.request.urlretrieve(url, "{}\{}".format(self.dirpath, filename))
        self.data_downloaded.emit('%s' % (self.urls))
