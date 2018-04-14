# -*- coding: utf-8 -*-

import cv2
import re
from collections import defaultdict

from PyQt5 import QtCore


class DetectorThread(QtCore.QThread):
    skins_detected = QtCore.pyqtSignal(object)

    def __init__(self, screen, skin_pathes, width, height):
        QtCore.QThread.__init__(self)
        self.screen = screen
        self.skin_pathes = skin_pathes
        self.width = width
        self.height = height

    def run(self):
        count = 0
        champ_skins = defaultdict(list)
        for skin_img_path in self.skin_pathes:
            search_image = cv2.imread(skin_img_path, 0)
            si_height, si_width = search_image.shape
            search_image = search_image[0:450, 0:si_width]
                
            resized_search_image = cv2.resize(search_image, (int(self.width*0.1), int(self.height*0.25)))
            resized_search_image = cv2.GaussianBlur(resized_search_image, (5, 5), 0)
    
            w, h = resized_search_image.shape[::-1]
                
            min_match_quality = 0.8
                
            method = eval('cv2.TM_CCOEFF_NORMED')
            res = cv2.matchTemplate(self.screen, resized_search_image, method)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                
            if max_val > min_match_quality:
                m = re.match(r".*\\(?P<champ_key>\d+)\_(?P<skin_num>\d+)\.png", skin_img_path)
                champ_skins[m.group('champ_key')].append(int(m.group('skin_num')))
                print(skin_img_path)
                count = count + 1
                
        champ_skins = dict(champ_skins)

        self.skins_detected.emit(champ_skins)
