# -*-coding:utf-8-*-

#客户端，登陆页面

import socket
import threading
import math
import sys
import tkinter.font as tkFont
import time
import tkinter as Tkinter
from tkinter.messagebox import *
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
from tkinter import filedialog
import re
import os

global nick
global clientSock


class Client_loginUI(object):
    local = '127.0.0.1'
    port = 8808
    global clientSock, nick

    def __init__(self, master = None):
        self.root = master
        self.root.iconbitmap('weixin.ico')

        self.sock = clientSock
        self.nick = ''
        self.createPage()

    def createPage(self):
        self.page = Tkinter.Frame(self.root)
        ft = tkFont.Font(family='微软雅黑', size=11)
        self.label = Tkinter.Label(self.page, text='Input nickname', height=2, font=ft)
        self.label.pack(expand=1, fill=Tkinter.BOTH)
        self.input = Tkinter.Text(self.page, width=50,height=1, font=tkFont.Font(family='微软雅黑', size=15))
        self.input.pack(expand=1, fill=Tkinter.BOTH)
        self.input.bind("<Return>", self.choose_nick)
        self.loginButton = Tkinter.Button(self.page, text='Login', width=10, command=self.choose_nick, font=ft,
                                          background='white',
                                          activebackground='black', activeforeground='white',
                                          )
        self.loginButton.pack(expand=1, side=Tkinter.BOTTOM and Tkinter.LEFT, padx=15, pady=8)
        self.exitButton = Tkinter.Button(self.page, text='Exit', width=10, command=self.page.quit, font=ft,
                                         background='white',
                                         activebackground='black', activeforeground='white',
                                         )
        self.exitButton.pack(expand=1, side=Tkinter.BOTTOM and Tkinter.RIGHT, padx=15, pady=8)
        # Tkinter.Button(self.page, text="Login", command=self.choose_nick).grid(row=1, column=0)
        # Tkinter.Button(self.page, text='Exit', command=self.page.quit).grid(row=1, column=1)
        self.page.pack(expand=1, fill=Tkinter.BOTH)

    def connect(self):
        try:
            self.sock.connect((self.local, self.port))
        except:
            showinfo(title='error', message='can\'t connect to server')
            os._exit(1)

    def choose_nick(self, _=None):
        global nick
        try:
            self.sock.getsockname()
        except:
            self.connect()
        self.nick = self.input.get('1.0',Tkinter.END).replace('\n', "")
        if self.nick == '':
            showinfo(title='error', message='invalid nickname')
        else:
            self.sock.sendall(bytes(self.nick, encoding='utf-8'))
            reply = str(self.sock.recv(1024), encoding="utf-8")
            if "nickname already exists." in reply:
                showinfo(title='error', message='invalid nickname')
            if "login successful!" in reply:
                nick = self.nick
                self.page.destroy()
                client = Client_mainUI(self.root)
                client.datain()




class Client_mainUI(object):
    global clientSock
    global nick
    def __init__(self, master=None):
        self.root = master
        self.root.iconbitmap('weixin.ico')
        self.frame = [Tkinter.Frame(),Tkinter.Frame(),Tkinter.Frame(),Tkinter.Frame()]
        self.nick = nick
        self.sock = clientSock
        self.outString = ''
        self.inString = ''
        self.root.title('Enjoy chatting, ' + self.nick)
        #显示消息Text右边的滚动条
        # self.chatTextScrollBar = Tkinter.Scrollbar(self.frame[0])
        # self.chatTextScrollBar.pack(side=Tkinter.RIGHT,fill=Tkinter.Y)

        #显示消息Text，并绑定上面的滚动条
        ft = tkFont.Font(family='微软雅黑',size=11)
        self.chatText = ScrolledText(self.frame[0],width=70,height=18,font=ft)
        self.chatText.pack(expand=1,fill=Tkinter.BOTH)
        self.frame[0].pack(expand=1,fill=Tkinter.BOTH)

        #标签，分开消息显示Text和消息输入Text
        label = Tkinter.Label(self.frame[1],height=1)
        label.pack(fill=Tkinter.BOTH)
        self.frame[1].pack(expand=1,fill=Tkinter.BOTH)

        #输入消息Text的滚动条
        # self.inputTextScrollBar = Tkinter.Scrollbar(self.frame[2])
        # self.inputTextScrollBar.pack(side=Tkinter.RIGHT,fill=Tkinter.Y)


        #输入消息Text，并与滚动条绑定
        ft = tkFont.Font(family='微软雅黑',size=11)
        self.inputText = ScrolledText(self.frame[2],width=70,height=8,font=ft)
        self.inputText.pack(expand=1,fill=Tkinter.BOTH)
        self.inputText.bind("<Control-Return>", self.dataout)
        self.frame[2].pack(expand=1,fill=Tkinter.BOTH)

        #发送消息按钮
        ft = tkFont.Font(family='微软雅黑', size=8)
        self.sendButton=Tkinter.Button(self.frame[3],text='Send (Ctrl+Enter)',width=15,height=2,font=ft,
                                       background='white',
                                       activebackground='black', activeforeground='white',
                                       command=self.dataout)
        self.sendButton.pack(expand=1, padx=15,pady=8, anchor=Tkinter.E)

        # 发送图片按钮
        # self.img_button = Tkinter.Button(self.frame[3], text='发送图片', width=10, command=self.send_image)
        # self.img_button.pack(expand=1, side=Tkinter.BOTTOM and Tkinter.LEFT, padx=15, pady=8)
        self.frame[3].pack(expand=1, fill=Tkinter.BOTH)

    def modified(self):
        self.chatText.yview_moveto(1)


    # 发送信息的函数
    def DealOut(self):
        temp = self.inputText.get('1.0',Tkinter.END)
        if re.sub('\s+', '', temp) == '':  # 整个输入都是空白字符
            showinfo(title='error', message='empty message!')

        else:
            self.outString = re.sub('\n+$', '', temp)
            self.outString = nick + ':' + self.outString  # 拼接cd
            try:
                self.sock.sendall(bytes(self.outString, encoding='utf-8'))  # 发送
            except:
                print("server error")
                showinfo(title='error', message='server error')
                os._exit(1)
            self.inputText.delete(0.0, self.outString.__len__() - 1.0)  # 发送完后清空输入框
    # 接收信息
    def DealIn(self):
        while True:
            try:
                self.inString = str(self.sock.recv(1024), encoding='utf-8')
                if not self.inString:
                    break
                """
                if "send an image" in self.inString:
                    while True:
                        temp = str(self.sock.recv(1024), encoding='utf-8')
                        if not temp:
                            break
                        self.inString += temp
                    self.inString = re.sub(r'^.*send an image', '', self.inString)
                    self.chatText.image_create(Tkinter.END, image=ImageTk.PhotoImage(data=self.inString))
                else:
                """


                if self.inString == self.outString:
                    self.inString = self.inString.replace(nick, "me", 1)
                theTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                try:
                    user, mess = self.inString.split(':', 1)
                    if user == 'robot':
                        self.chatText.tag_config("tag_1", foreground="blue")
                        self.chatText.insert(Tkinter.END, user + ':' + theTime + '\n', 'tag_1')
                        self.chatText.insert(Tkinter.END, mess + '\n\n', 'tag_1')
                    else:
                        self.chatText.insert(Tkinter.END, user + ':' + theTime + '\n')
                        self.chatText.insert(Tkinter.END, mess + '\n\n')
                    self.modified()
                except:
                    self.chatText.insert(Tkinter.END, theTime + ' \n')
                    self.chatText.insert(Tkinter.END, self.inString + '\n\n')
                    self.modified()


                print(self.inString)
            except:
                break

    def datain(self):
        thin = threading.Thread(target=self.DealIn)  # 调用threading 创建一个接收信息的线程'
        thin.start()

    def dataout(self, _=None):
        thout = threading.Thread(target=self.DealOut)  # 创建一个发送信息的线程，声明是一个元组
        thout.start()

"""
    def send_image(self):
        filename = filedialog.askopenfilename(filetypes=[("Image Files",
                                                          ["*.jpg", "*.jpeg", "*.png", "*.gif", "*.JPG", "*.JPEG",
                                                           "*.PNG", "*.GIF"]),
                                                         ("All Files", ["*.*"])])
        if filename is None or filename == '':
            return
        with open(filename, "rb") as imageFile:
            f = imageFile.read()
            b = bytes(f)
            try:
                senddata = bytes(self.nick+":flag=1", encoding='utf-8')
                self.sock.sendall(senddata)
                self.sock.sendall(b)

            except:
                print("server error")
                sys.exit()
"""


def quit():
    os._exit(0)

if __name__=='__main__':
    try:
        clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except:
        print("Failed to create socket.")
        sys.exit()

    root = Tkinter.Tk()
    root.title('Python在线聊天-客户端登录')
    Client_loginUI(root)
    root.protocol("WM_DELETE_WINDOW", quit)
    root.mainloop()





