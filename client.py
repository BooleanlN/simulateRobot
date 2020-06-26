#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Py40 PyQt5 tutorial

This program creates a skeleton of
a classic GUI application with a menubar,
toolbar, statusbar, and a central widget.

author: Jan Bodnar
website: py40.com
last edited: January 2015
"""

import sys
from concurrent.futures import ProcessPoolExecutor,ThreadPoolExecutor
import time
from functools import partial

from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QApplication,QTableWidget,QTableWidgetItem,QPushButton,QComboBox,QProgressBar,QFileDialog,QLabel,QGridLayout,QLineEdit
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QFont, QColor, QBrush, QPixmap
from PyQt5.QtCore import Qt,QThread,QThreadPool
import pandas as pd
import numpy as np
from selenium.common.exceptions import  NoSuchWindowException

from proxycrawler import simulate_browser
import images

class Example(QMainWindow):

    def __init__(self):
        super().__init__()
        self._usertable = []
        self._result = {self._usertable[i][2]:0 for i in range(len(self._usertable))}
        self.initUI()
        # self.threadPool = ThreadPoolExecutor()
        # self.futures = []

    def initUI(self):
        # textEdit = QTextEdit()
        upload =self.upload_widget()
        # about_p = self.about_widget()
        self.setCentralWidget(upload)

        # 工具栏
        exitAction = QAction(QIcon('./assets/img/quit.png'), '退出', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('退出程序')
        exitAction.triggered.connect(self.close)

        aboutAction = QAction(QIcon('./assets/img/aboutus.png'), '关于', self)
        aboutAction.setShortcut('Ctrl+A')
        aboutAction.setStatusTip('关于我们')
        aboutAction.triggered.connect(self.about_widget)

        # settingAction = QAction(QIcon('./assets/img/setting.png'), '设置', self)
        # settingAction.setShortcut('Ctrl+S')
        # settingAction.setStatusTip('设置')
        homeAction =QAction(QIcon('./assets/img/home.png'), '主页', self)
        homeAction.setShortcut('Ctrl+H')
        homeAction.setStatusTip('主页')
        homeAction.triggered.connect(self.tohome)

        logAction = QAction(QIcon('./assets/img/log.png'), '日志', self)
        logAction.setShortcut('Ctrl+L')
        logAction.setStatusTip('日志')
        logAction.triggered.connect(self.show_logs)

        self.statusBar().showMessage('Ready')

        toolbar = self.addToolBar('Exit')

        toolbar.addAction(homeAction)
        toolbar.addAction(aboutAction)
        # toolbar.addAction(settingAction)
        toolbar.addAction(logAction)
        toolbar.addAction(exitAction)

        self.setGeometry(300, 300, 1000, 500)
        self.setWindowTitle('Main window')
        self.show()

    def table_layout(self):
        horizontalHeader = ["序号","姓名","学号","密码","专业","视频个数","操作","进度"]
        table = QTableWidget()
        table.setColumnCount(8)
        table.setRowCount(len(self._usertable))

        table.setHorizontalHeaderLabels(horizontalHeader)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)

        for index in range(table.columnCount()):
            headItem = table.horizontalHeaderItem(index)
            headItem.setFont(QFont("song", 12, QFont.Bold))
            headItem.setForeground(QBrush(Qt.gray))
            headItem.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        table.setColumnWidth(4, 100)
        table.setRowHeight(0, 40)
        for i,user_item in enumerate(self._usertable):
            print(user_item)
            for index,item in enumerate(user_item):
                print(item)
                table.setItem(i, index, QTableWidgetItem(str(item)))
            beginBtn = QPushButton('开始')
            # beginBtn.setDown(True)
            beginBtn.setStyleSheet('QPushButton{margin:3px}')
            table.setCellWidget(i, 6, beginBtn)
            pbar = QProgressBar()
            # pbar.setValue(self._result[i])
            beginBtn.clicked.connect(partial(self.do_study,i,10))
            table.setCellWidget(i, 7, pbar)
            nbset = QLineEdit()
            nbset.editingFinished.connect(partial(self.set_videoNum,nbset.text(),i))
            nbset.setText('10')
            table.setCellWidget(i, 5, nbset)
        return table
    def set_videoNum(self,num,index):
        # print(self._usertable[index])
        # print(num,index)
        self._usertable[index][len( self._usertable[index])-1]=num
        #self._usertable[index].insert(num)
        self.write2log("设置学生{}看视频个数为{}".format(self._usertable[index][1],num))
    def about_widget(self):
        about = QTextEdit()
        texts = ["{}：{}".format(username,result) for username,result in self._result.items() ]
        about.setText("关于：xxxx\n"+"\n".join(texts))
        self.change_panel(about)
    def do_study(self,i,num):
        print(self._usertable[i])
        #future = self.threadPool.submit(simulate_browser,(None,self._usertable[i][2],self._usertable[i][3]))
        mythread = MyThread("thread{}".format(i),self._usertable[i][2],self._usertable[i][3],None,num,self._result)
        mythread.start()
        mythread.exec()
        self.write2log("{}开始学习".format(self._usertable[i][2]))
        # self.futures.append(future)
        # print(future.running())
        #simulate_browser(None,self._usertable[i][2],self._usertable[i][3])
    def change_panel(self,changeWidget):
        self.setCentralWidget(changeWidget)
    def upload_widget(self):
        upload_btn = QPushButton("上传学生数据")
        upload_btn.setFixedSize(150,40)
        upload_btn.clicked.connect(self.openfile)
        return upload_btn
    def openfile(self):
        self.write2log("上传学生数据")
        openfile_name = QFileDialog.getOpenFileName(self, '选择文件', '', 'Excel files(*.xlsx , *.xls)')
        self._usertable = get_users(openfile_name[0])
        # self._result = [0 for i in range(len(self._usertable))]
        self._result = {self._usertable[i][2]: 0 for i in range(len(self._usertable))}
        table = self.table_layout()
        self.change_panel(table)
    def show_logs(self):
        print("查看日志")
        text = QTextEdit()
        logs = ""
        with open("log.txt") as log:
            logs = log.readlines()

        text.setText("日志内容：\n"+"".join(logs))
        self.change_panel(text)
    def tohome(self):
        if(len(self._usertable) > 0):
            table = self.table_layout()
            self.change_panel(table)
        else:
            upload = self.upload_widget()
            self.change_panel(upload)
    def write2log(self,text):
        """写入日志"""
        with open("log.txt","a+",encoding="utf8") as f:
            f.write(time.strftime("%Y-%m-%d %H:%M:%S\t", time.localtime())+text+"\n")
class MyThread(QThread):
    def __init__(self,name,username,password,proxy,num,result):
        super(MyThread,self).__init__()
        self.name = name
        self.username = username
        self.password = password
        self.proxy = proxy
        self.num = num
        self.result = result
    def run(self):
        print("start....{}".format(self.username))
        self.write2log("start....{}".format(self.username))
        try:
            result = simulate_browser(self.proxy,self.username,self.password,self.result,self.num)
        except NoSuchWindowException as e:
            print("异常：",e)
            self.write2log("账号{}出现Nosuchwindow异常：{}".format(self.username,e))
        except Exception as e2:
            self.write2log("账号{}出现异常：{}".format(self.username, e2))
        finally:
            print("账号{}因账号错误退出".format(self.username))
            self.write2log("账号{}因账号错误退出".format(self.username))
            self.exit()
    def write2log(self,text):
        """写入日志"""
        with open("log.txt","a+",encoding="utf8") as f:
            f.write(time.strftime("%Y-%m-%d %H:%M:%S\t", time.localtime())+text+"\n")
def get_users(path):
    users = pd.read_excel(path,header=0,names=["序号","姓名","学号","密码","专业"])
    return users.values
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())

    # print(users.values[1])