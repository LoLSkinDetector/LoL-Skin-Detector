# -*- coding: utf-8 -*-

import cv2
import numpy as np


class ImagesJoiner():
    def __init__(self, screens_pathes):
        self.screens_pathes = screens_pathes
        self.screens_count = len(self.screens_pathes)
        self.screen = self.join_images()
        self.screen = cv2.medianBlur(self.screen, 9)
        
    def join_images(self):
        main_image = self.screens_pathes[0]

        main_image_path = True
        if self.screens_count > 1:
            for screen in self.screens_pathes[1:]:
                if main_image_path:
                    img1 = cv2.imread(main_image, 0)
                    self.height, self.width = img1.shape
                    
                    img2 = cv2.imread(screen, 0)
                    new_img = np.concatenate((img1, img2), axis=0)
                    main_image = new_img
                    main_image_path = False
                else:
                    img1 = main_image
                    img2 = cv2.imread(screen, 0)
                    new_img = np.concatenate((img1, img2), axis=0)
                    main_image = new_img
            return main_image
        
        main_image = cv2.imread(main_image, 0)
        self.height, self.width = main_image.shape
        return main_image