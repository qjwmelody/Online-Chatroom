# -*-coding:utf-8-*-

#服务端

import socket
import threading
import math
import tkinter.font as tkFont
import time
import tkinter as Tkinter
import urllib
import json
import sys
import importlib
importlib.reload(sys)
import string
from urllib import parse
from urllib import request
import re
from tkinter.scrolledtext import ScrolledText
import os
from tkinter.messagebox import *

class ServerUI():
    title = 'Python在线聊天-服务器端'
    local = '127.0.0.1'
    port = 8808
    global serverSock
    global data

    def __init__(self):
        self.root = Tkinter.Tk()
        self.root.iconbitmap('weixin.ico')
        self.root.title(self.title)
        self.data = ''
        self.nick_list = []
        self.con = threading.Condition()  # 条件
        self.buffer = 1024
        # 窗口面板，用4个frame布局
        self.frame = [Tkinter.Frame(), Tkinter.Frame()]

        # 显示消息Text右边的滚动条
        # self.chatTextScrollBar = Tkinter.Scrollbar(self.frame[0])
        # self.chatTextScrollBar.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)

        # 显示消息Text,并绑定上面的滚动条
        ft = tkFont.Font(family='微软雅黑', size=11)
        self.chatText = ScrolledText(self.frame[0], width=70, height=18, font=ft)
        self.chatText.pack(expand=1, fill=Tkinter.BOTH)
        self.frame[0].pack(expand=1, fill=Tkinter.BOTH)

        # 标签，分开消息显示Text和消息输入Text
        label = Tkinter.Label(self.frame[1], height=2)
        label.pack(fill=Tkinter.BOTH)
        self.frame[1].pack(expand=1, fill=Tkinter.BOTH)
        """
        # 输入消息Text的滚动条
        self.inputTextScrollBar = Tkinter.Scrollbar(self.frame[2])
        self.inputTextScrollBar.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)

        # 输入消息Text，并与滚动条绑定
        ft = tkFont.Font(family='微软雅黑', size=11)
        self.inputText = Tkinter.Text(self.frame[2], width=70, height=8, font=ft)
        self.inputText['yscrollcommand'] = self.inputTextScrollBar.set
        self.inputText.pack(expand=1, fill=Tkinter.BOTH)
        self.inputTextScrollBar['command'] = self.chatText.yview()
        self.frame[2].pack(expand=1, fill=Tkinter.BOTH)
        """


    def modified(self):
        self.chatText.yview_moveto(1)

    def clientThreadIn(self, conn, nick):
        while True:
            try:
                temps = str(conn.recv(1024), encoding='utf-8')  # 客户端发过来的消息
                if not temps:
                    conn.close()
                    return
                self.NotifyAll(temps)
                theTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                user, mess = self.data.split(':', 1)
                self.chatText.insert(Tkinter.END, user + ':' + theTime + '\n')
                self.chatText.insert(Tkinter.END, mess + '\n\n')
                self.modified()
                print(self.data)
                if "@robot" in self.data:
                    question = re.sub('^.*:', '', self.data)
                    question = re.sub('\n', '', question)
                    question = re.sub('@robot', '', question)
                    result = self.get_computer_tuling(question)
                    if len(result) == 0:
                        result = "EXD"
                    self.NotifyAll(result)



            except:
                self.NotifyAll(nick + ' leaves the room')  # 出现异常就退出
                self.nick_list.remove(nick)
                theTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                self.chatText.insert(Tkinter.END, theTime + '\n')
                self.chatText.insert(Tkinter.END, self.data + '\n\n')
                self.modified()
                print(self.data)
                return

    def clientThreadOut(self, conn, nick):
        while True:
            if self.con.acquire():
                self.con.wait()  # 堵塞，放弃对资源的占有  等待通知运行后面的代码
                if self.data:
                    try:
                        conn.send(bytes(self.data, encoding='utf-8'))
                        self.con.release()
                    except:
                        self.con.release()
                        return

    def NotifyAll(self, ss):
        if self.con.acquire():  # 获取锁
            self.data = ss
            self.con.notifyAll()  # 当前线程放弃对资源的占有，通知所有等待x线程
            self.con.release()

    # 开启服务器
    def start(self):
        try:
            self.serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except:
            print("Failed to create socket.")
            showinfo(title='error', message='fail to create socket!')
            os._exit(1)
        self.chatText.insert(Tkinter.END, 'Socket created..\n')
        try:
            self.serverSock.bind((self.local, self.port))
        except:
            showinfo(title='error', message='Address already occupied!')
            os._exit(1)
        self.chatText.insert(Tkinter.END, 'Socket now listening..\n')
        self.serverSock.listen(5)

        while True:
            self.connection, self.address = self.serverSock.accept()  # 接受连接
            print('Connected with' + ' ' + self.address[0] + ':' + str(self.address[1]))  # 字符串拼接
            self.chatText.insert(Tkinter.END, 'Connected with ' + self.address[0] + ':' + str(self.address[1]) + '\n\n')
            self.modified()
            nick = str(self.connection.recv(self.buffer), encoding='utf-8')  # 获取用户名
            while nick in self.nick_list or 'robot' in nick:
                self.connection.sendall(bytes("nickname already exists.", encoding='utf-8'))
                nick = str(self.connection.recv(self.buffer), encoding="utf-8")
            self.nick_list.append(nick)
            self.connection.sendall(bytes("login successful!", encoding='utf-8'))
            self.NotifyAll('Welcome' + ' ' + nick + ' to the room!')
            theTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            self.chatText.insert(Tkinter.END, theTime + '\n')
            self.chatText.insert(Tkinter.END, self.data + '\n')
            print(self.data)
            self.chatText.insert(Tkinter.END, str(len(self.nick_list)) + ' person(s)\n\n')
            self.modified()
            print(str(len(self.nick_list)) + ' person(s)')
            self.connection.sendall(bytes(self.data, encoding='utf-8'))
            threading.Thread(target=self.clientThreadIn, args=(self.connection, nick)).start()
            threading.Thread(target=self.clientThreadOut, args=(self.connection, nick)).start()



    def startServer(self):
        s = threading.Thread(target=self.start)
        s.start()

    def get_computer_tuling(self, info):
        """
        key = 'a0ea872b4f564ff08f2fe3e74f083e67'
        api = 'http://openapi.tuling123.com/openapi/api/v2'
        dat = {
            "perception": {
                "inputText": {
                    "text": info
                }
            },
            "userInfo": {
                "apiKey": key,
                "userId": '368605'
            }
        }
        dat = json.dumps(dat)
        response = urllib.request.urlopen(api, data=dat).read()
        response = response.decode('utf-8')
        dic_json = json.loads(response)
        message = 'robot:'.encode('utf-8').decode('utf-8') + dic_json['text'] + '\n'
        """
        key = '186cccedc79549ecac4dcc8a56fc9fb4'
        api = 'http://www.tuling123.com/openapi/api?key=' + key + '&info=' + info
        api = urllib.parse.quote(api, safe=string.printable)
        response = urllib.request.urlopen(api).read()
        response = response.decode('utf-8')
        dic_json = json.loads(response)

        message = 'robot:'.encode('utf-8').decode('utf-8') + dic_json['text']
        theTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        user, mess = message.split(':', 1)
        self.chatText.insert(Tkinter.END, user + ':' + theTime + '\n')
        self.chatText.insert(Tkinter.END, mess+'\n\n')
        self.modified()
        return message

def main():
    server = ServerUI()
    server.startServer()
    server.root.protocol("WM_DELETE_WINDOW", quit)
    server.root.mainloop()

def quit():
    os._exit(0)

if __name__ == '__main__':
    main()

"""
win = tk.Tk()
win.title("server")
win.geometry("400x400+200+20")


def clientThreadIn(self, conn, nick):
    global data
    while True:
        try:
            temp = conn.recv(1024)  # 客户端发过来的消息
            if not temp:
                conn.close()
                return
            self.NotifyAll(str(temp, encoding='utf-8'))
            self.textBrowser.append(data)
            print(data)

        except:
            self.NotifyAll(nick + ' leaves the room')  # 出现异常就退出
            self.textBrowser.append(data)
            print(data)
            return


def clientThreadOut(self, conn, nick):
    global data
    while True:
        if self.con.acquire():
            self.con.wait()  # 堵塞，放弃对资源的占有  等待通知运行后面的代码
            if data:
                try:
                    conn.send(bytes(data, encoding='utf-8'))
                    self.con.release()
                except:
                    self.con.release()
                    return


def NotifyAll(self, ss):
    global data
    if self.con.acquire():#获取锁
            data = ss
            self.con.notifyAll()#当前线程放弃对资源的占有，通知所有等待x线程
            self.con.release()

con = threading.Condition()#条件

def start():
    Host = eip.get()  # ip地址
    port = int(eport.get())
    data = ''

    try:
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)#创建套接字,默认为ipv4
    except:
        print("Failed to create socket.")
        sys.exit()
    # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建套接字
    print('Socket created')
    s.bind((Host, port))  # 把套接字绑定到ip地址
    s.listen(5)
    print('Socket now listening')
    nick_list = []
    while True:
        conn, addr = s.accept()  # 接受连接
        print('Connected with'+' ' + addr[0]+':'+str(addr[1]))  # 字符串拼接
        nick = str(conn.recv(1024), encoding='utf-8')  # 获取用户名
        while(nick in nick_list):
            conn.sendall(bytes("nickname already exists.", encoding='utf-8'))
            nick = str(conn.recv(1024), encoding="utf-8")
        nick_list.append(nick)
        conn.sendall(bytes("login successful!", encoding='utf-8'))
        NotifyAll('Welcome'+' '+nick + ' to the room!')
        print(data)
        print(str(math.ceil((threading.activeCount()+1)/2))+' person(s)')
        conn.sendall(bytes(data, encoding='utf-8'))
        threading.Thread(target=clientThreadIn, args=(conn, nick)).start()
        threading.Thread(target=clientThreadOut,args=(conn, nick)).start()

def startServer():
    s = threading.Thread(target=start)
    s.start()

labelIP = tkinter.Label(win, text='ip').grid(row=0, column=0)
labelPort = tkinter.Label(win, text='port').grid(row=1, column=0)
eip = tkinter.Variable()
eport = tkinter.Variable()
entryIp = tkinter.Entry(win, textvariable=eip).grid(row=0, column=1)
entryPort = tkinter.Entry(win, textvariable=eport).grid(row=1, column=1)
button = tkinter.Button(win, text="启动", command=startServer).grid(row=2, column=0)
text = tkinter.Text(win, height=5, width=30)
labeltext = tkinter.Label(win, text='连接消息').grid(row=3, column=0)
text.grid(row=3, column=1)

"""