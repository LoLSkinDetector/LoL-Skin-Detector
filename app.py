# -*- coding: utf-8 -*-

import sys
import os
import shutil
import glob

from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QPushButton, QProgressBar, QAction, QMessageBox, QMenuBar, QSystemTrayIcon, QLabel
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSize

from download_skins import DownloadSkins, DownloadThread
from utility_functions import each_slice
from detect_skins import DetectorThread
from images_joiner import ImagesJoiner
 

class App(QWidget):
    SKINS_DIR_NAME = "skins"
    ICONS_DIR_NAME = "icons"
    BUTTON_WIDTH = 100
    BUTTON_HEIGHT = 30
 
    def __init__(self):
        super().__init__()
        self.title = 'LoL Skin Detector'
        self.left = 100
        self.top = 100
        self.width = 365
        self.height = 300
        self.dirpath = os.getcwd()
        self.skins_dir_path = "{}\{}".format(self.dirpath, self.SKINS_DIR_NAME)
        self.icons_dir_path = "{}\{}".format(self.dirpath, self.ICONS_DIR_NAME)
        self.skins_pathes = glob.glob(r"{}\*".format(self.skins_dir_path))
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        manualAction = QAction("&Manual", self)
        manualAction.setShortcut("Ctrl+M")
        manualAction.setStatusTip('Open manual')
        manualAction.triggered.connect(self.showManual)
        
        app_icon = QIcon()
        print(r"{}\16x16.png".format(self.icons_dir_path))
        app_icon.addFile(r"{}\16x16.png".format(self.icons_dir_path), QSize(16, 16))
        app_icon.addFile(r"{}\32x32.png".format(self.icons_dir_path), QSize(32, 32))
        app_icon.addFile(r"{}\64x64.png".format(self.icons_dir_path), QSize(64, 64))
        self.setWindowIcon(app_icon)
        
        picture = QLabel(self)
        picture.setGeometry(185, 50, 130, 130)
        picture.setPixmap(QPixmap(r"{}\130x130.png".format(self.icons_dir_path)))
  
        self.mainMenu = QMenuBar(self)
        infoMenu = self.mainMenu.addMenu("&Info")
        infoMenu.addAction(manualAction)    
        
        self.btnDownloadSkins = QPushButton("Download Skins", self)
        self.btnDownloadSkins.setGeometry(50, 50, self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
        self.btnDownloadSkins.clicked.connect(self.btnClickedDownloadSkins)
        
        self.btnLoadScreenshots = QPushButton("Load Screenshots", self)
        self.btnLoadScreenshots.setGeometry(50, 100, self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
        self.btnLoadScreenshots.clicked.connect(self.btnClickedLoadScreenshots)
        
        self.btnDetectSkins = QPushButton("Detect Skins", self)
        self.btnDetectSkins.setGeometry(50, 150, self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
        self.btnDetectSkins.clicked.connect(self.btnClickedbtnDetectSkins)
        self.btnDetectSkins.setEnabled(False)
        
        self.progressBar = QProgressBar(self)
        self.progressBar.setGeometry(50, 200, 300, 20)
        
        self.setFixedSize(self.size())
 
        self.show()
        
    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
        
    def showManual(self):
        QMessageBox.about(self, "Manual", "How to use:\n1) Click \"Download Skins\" button to download skins.\n2) Click \"Load Screenshots\" button and select your screenshots.\n\tPelase use Alt+PrtScr to capture screenshots.\n3) Click \"Detect Skins\" button.")
        
    def btnClickedDownloadSkins(self):
        images_count_per_thread = 40
        self.threads = []
        self.completion_percent = 0
        self.progressBar.setValue(self.completion_percent)
        
        if not os.path.exists(self.SKINS_DIR_NAME):
            os.makedirs(self.SKINS_DIR_NAME)
        else:
            shutil.rmtree(self.SKINS_DIR_NAME)
            os.makedirs(self.SKINS_DIR_NAME)
                
        all_skins = DownloadSkins()
        all_urls = all_skins.fetch_loading_skin_urls()
        sliced_urls = each_slice(all_urls, images_count_per_thread)
        
        self.additional_percent = round((100 / (int(len(all_urls) / images_count_per_thread)) / 2), 3)
        
        for urls in sliced_urls:
            if self.completion_percent < 100:
                self.completion_percent += self.additional_percent
                self.progressBar.setValue(self.completion_percent)
            downloader = DownloadThread(urls, self.skins_dir_path)
            print(self.skins_dir_path)
            downloader.data_downloaded.connect(self.on_data_ready)
            self.threads.append(downloader)
            downloader.start()
            
    def on_data_ready(self, data):
        if self.completion_percent < 100:
            self.completion_percent += self.additional_percent
            self.progressBar.setValue(self.completion_percent)        
         
    def btnClickedbtnDetectSkins(self):
        skins_count_per_thread = 200
        self.threads = []
        self.completion_percent = 0
        self.progressBar.setValue(self.completion_percent)
        self.detected_skins = {}

        sliced_skins_pathes = each_slice(self.skins_pathes, skins_count_per_thread)
        
        self.additional_percent = round((100 / (int(len(self.skins_pathes) / skins_count_per_thread)) / 2), 3)
                
        for skins_pathes in sliced_skins_pathes:
            if self.completion_percent < 100:
                self.completion_percent += self.additional_percent
                self.progressBar.setValue(self.completion_percent)
            detector = DetectorThread(self.screen, skins_pathes, self.screen_chunk_width, self.screen_chunk_height)
            detector.skins_detected.connect(self.on_skins_detected)
            self.threads.append(detector)
            detector.start()

    def on_skins_detected(self, data):
        if self.completion_percent < 100:
            self.completion_percent += self.additional_percent
            self.progressBar.setValue(self.completion_percent)
        print(data)
        print(isinstance(data, dict))
        print(self.detected_skins)
        self.detected_skins.update(data)
        
    def btnClickedLoadScreenshots(self):
        self.progressBar.reset()
        self.files = self.openFileNamesDialog()
        images_joiner = ImagesJoiner(self.files)
        self.screen = images_joiner.screen
        self.screen_chunk_width = images_joiner.width
        self.screen_chunk_height = images_joiner.height
        self.btnDetectSkins.setEnabled(True)
        
    def openFileNamesDialog(self):    
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self,"QFileDialog.getOpenFileNames()", "","Images (*.png *.jpg);;All Files (*)", options=options)
        if files:
            return files
 


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()

    sys.exit(app.exec_())