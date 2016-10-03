#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import subprocess
import time
import os
import signal
import pyatspi
from threading import Thread
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QShortcut, QSystemTrayIcon, QMenu
from PyQt5 import QtGui, QtCore
global proc
global vlc

class Monitor:
	def keylisten_cb(self, event):
		if event.type == pyatspi.KEY_PRESSED_EVENT:
			#print(event)
			if event.event_string == "Control_L":
				self.history = event.event_string
			if event.event_string == "F9" and self.history == "Control_L":
				self.history = ""
				main.start()

			if event.event_string == "F10" and self.history == "Control_L":
				self.history = ""
				main.stop()
		

	def __init__(self):
		self.reg = pyatspi.Registry
		#self.reg.registerKeystrokeListener(self.keylisten_cb, mask=pyatspi.allModifiers())
		self.reg.registerKeystrokeListener(self.keylisten_cb, kind=(pyatspi.KEY_PRESSED_EVENT, pyatspi.KEY_RELEASED_EVENT), mask=pyatspi.allModifiers())
		self.history = None

	def start(self):
		self.reg.start()

class Process(Thread):
	def __init__(self):
		Thread.__init__(self)
	def run(self):
		global proc
		timestamp = time.strftime("%Y-%m-%d_%H%M%S")
		vlc  = 'vlc','-I','dummy','screen://','--screen-fps=25','--screen-follow-mouse','--one-instance','--no-video','--sout','#transcode{vcodec=mp4v,vb072}:standard{access=file,mux=mp4,dst=./Screencast-' + timestamp + '.mp4}'
		ffmpeg = 'ffmpeg', '-f', 'x11grab', '-s', '1366x768', '-r', '25', '-i', ':0.0', '-c:v', 'mpeg4', '-f', 'avi', '-q:v', '0', './Screencast-' + timestamp + '.avi'
		proc = subprocess.Popen(ffmpeg)
		btnStart.setEnabled(False)
		btnStop.setEnabled(False)
		main.icon.setIcon(QtGui.QIcon("./icons/record.png"))
		time.sleep(5)
		btnStop.setEnabled(True)

	def stop(self):
		print(proc.pid)
		os.kill(proc.pid, signal.SIGINT)
		main.icon.setIcon(QtGui.QIcon("./icons/idle.png"))
		btnStart.setEnabled(True)
		btnStop.setEnabled(False)

class Main(QWidget):

	def __init__(self):
		super(Main, self).__init__()
		self.initUI()

	def initUI(self):
		global btnStart
		btnStart = QPushButton('Запись', self)
		btnStart.resize(100, 50)
		btnStart.move(1, 10)
		btnStart.clicked.connect(self.start)
		global btnStop
		btnStop = QPushButton('Стоп', self)
		btnStop.resize(100,50)
		btnStop.move(100,10)
		btnStop.clicked.connect(self.stop)
		btnStop.setEnabled(False)
		self.setGeometry(60,60,200,60)
		self.setWindowTitle('Screencaster')
		self.setWindowIcon(QtGui.QIcon("./icons/idle.png"))

		self.icon = QSystemTrayIcon()
		self.icon.setIcon(QtGui.QIcon("./icons/idle.png"))
		self.icon.show()
		self.icon.activated.connect(self.__icon_activated)

		self.trayIconMenu = QMenu()
		recMenu = self.trayIconMenu.addAction("Запись (Ctrl_L+F9)")
		recMenu.triggered.connect(self.start)
		stopMenu = self.trayIconMenu.addAction("Стоп (Ctrl_L+F10)")
		stopMenu.triggered.connect(self.stop)
		self.trayIconMenu.addSeparator()
		exitMenu = self.trayIconMenu.addAction("Выход")
		exitMenu.triggered.connect(self.exitAction)
		self.icon.setContextMenu(self.trayIconMenu)
	
	def start(self):
		global process
		process = Process()
		process.start()
	
	def stop(self):
		process.stop()

	def closeEvent(self,event):
		main.stop()
		event.accept()

	def __icon_activated(self, reason):
		if reason == QSystemTrayIcon.Trigger: # or DoubleClick
			if self.isHidden() == True:
				self.show()
			else:
				self.hide()

	def exitAction(self):
		main.stop()
		sys.exit()

if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = Main()
	monitor = Monitor()
	sys.exit(app.exec_())


