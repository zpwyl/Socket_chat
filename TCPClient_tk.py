# !/usr/bin/env python3
# _*_ utf-8 _*_
# @Time    : 2018/10/13/013 18:25
# @File    : TCPClient1.py
# @Software: PyCharm
# @author = zp



"""
配置文件
消息长度（大端对齐）尚未实现
消息和目的用户都用json.dumps()表示
收到的消息形式 日期,收信人,消息
发送的消息形式 日期,发信人,消息$
"""

MAX_USER = 20               # 最大用户数
SERVER_PORT = 8080          # 服务器端口号
MSG_LENS_SIZE = 1024        # 1024B 消息长度
MESSAGE_DISTINGUISH = ','   #消息分隔目的用户和消息的符号
MESSAGE_BETWEEN = '$'       #消息之间的区分的符号


from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import tkinter


def rec_message(rec_asp, text):
    '''接收数据'''
    try:
        message = []
        info = rec_asp.recv(MSG_LENS_SIZE).decode('utf-8')
        if info:
            message.append(info)
        messages = ''.join(message)
        message_num = messages.count(MESSAGE_BETWEEN)
        for i in range(message_num):
            mes = messages.split(MESSAGE_BETWEEN)[i]
            to_username, data = mes.split(MESSAGE_DISTINGUISH)[0], mes.split(MESSAGE_DISTINGUISH)[1]
            mess = ('{}：{}\n'.format(to_username, data))
            text.insert(tkinter.INSERT, mess)
    except:
        pass



def send_message(client, message, to_username, text):
    client_transmit = message.get()
    mit_username = to_username.get()
    to_message = mit_username + MESSAGE_DISTINGUISH + client_transmit
    text.insert(tkinter.INSERT, '我对'+mit_username+'：'+client_transmit+'\n')
    message.set('')
    client.send(to_message.encode('utf-8'))
    print('发送成功')


def start_client(win, username):
    win.destroy()
    client = socket(AF_INET, SOCK_STREAM)
    client.connect(('127.0.0.1', SERVER_PORT))
    client.send((username.get()).encode('utf-8'))
    wins = tkinter.Tk()
    wins.title('Client')
    wins.geometry('600x400+400+200')
    lable1 = tkinter.Label(wins, text='收信人', width=10)
    lable1.place(x=0, y=0)
    # list_name = tkinter.Listbox(wins, width=10, height=17, selectmode=tkinter.BROWSE)
    # list_name.place(x=0, y=20)
    # def set_list_name(event):
    #     list_name.select_set(list_name.curselection())
    #     lable2 = tkinter.Label(wins, text='正在和' + list_name.get(list_name.curselection()) + '聊天', width=10)
    #     lable2.place(x=80, y=0)
    # for item in ['ll', 'zz', 'pp', 'yy', 'gg']:
    #     list_name.insert(tkinter.END, item)
    # list_name.bind('<Double-Button-1>', set_list_name)
    username = tkinter.Variable()
    text_entry = tkinter.Entry(wins, textvariable=username, width=10)
    text_entry.place(x=0, y=20)
    message = tkinter.Variable()
    text_entry = tkinter.Entry(wins, textvariable=message, width=60)
    text_entry.place(x=80, y=305)
    text = tkinter.Text(wins, width=70, height=21)
    text.place(x=80, y=23)
    button = tkinter.Button(wins, text='发送', width=8, height=1, command=lambda: send_message(client, message, username, text))
    button.place(x=510, y=300)
    g = Thread(target=s, args=(client, text,))
    g.start()
    wins.mainloop()


def s(client, text):
    try:
        while True:
            rec_message(client, text)
            print('收到消息')
    except:
        client.close()
        print('客户端关闭')


def start_view():
    win = tkinter.Tk()
    win.title('Login')
    win.geometry('400x400+400+200')
    username = tkinter.Variable()
    username_entry = tkinter.Entry(win, textvariable=username)
    username_entry.pack()
    button = tkinter.Button(win, text='登录', command=lambda: start_client(win, username))
    button.pack()
    win.mainloop()


if __name__ =='__main__':
    start_view()