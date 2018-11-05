# !/usr/bin/env python3
# _*_ utf-8 _*_
# @Time    : 2018/10/12/012 19:31
# @File    : TCPServer.py
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
from threading import Thread, Lock
import tkinter


def rec_message(userid_mapping, username, log_text, MQ):
    '''接收数据'''
    while True:
        try:
            rec_asp = userid_mapping[username]
            message = []
            info = rec_asp.recv(MSG_LENS_SIZE).decode('utf-8')
            if info:
                message.append(info)
            messages = ''.join(message)
            try:
                to_username, date = messages.split(MESSAGE_DISTINGUISH)[0], messages.split(MESSAGE_DISTINGUISH)[1]
                log = ('{}发送给你数据：{}\n'.format(username, date))
                log_text.insert(tkinter.INSERT, log)
            except:
                to_username, date = '', ''
            lock = Lock()
            message = username + MESSAGE_DISTINGUISH + date + MESSAGE_BETWEEN
            if to_username in userid_mapping.keys():
                log = ('{}在线，消息传递成功\n'.format(to_username))
                log_text.insert(tkinter.INSERT, log)
                userid_mapping[to_username].send(message.encode('utf-8'))
            else:
                log = ('{}不在线，消息已存入队列\n'.format(to_username))
                log_text.insert(tkinter.INSERT, log)
                lock.acquire()
                MQ.setdefault(to_username, [])
                MQ[to_username].append(message)
                lock.release()
        except:
            pass


def get_username(clientSocker):
    message = []
    info = clientSocker.recv(MSG_LENS_SIZE).decode('utf-8')
    if info:
        message.append(info)
    messages = ''.join(message)
    return messages


def MQ_send_message(to_username, userid_mapping, MQ, log_text):
    messages = MQ[to_username]
    for mess in messages:
        userid_mapping[to_username].send(mess.encode('utf-8'))
    del MQ[to_username]
    log = ('{}的消息已发送\n'.format(to_username))
    log_text.insert(tkinter.INSERT, log)


def start(server, userid_mapping, MQ, log_text):
    server.bind(('127.0.0.1', SERVER_PORT))
    server.listen(MAX_USER)
    log = '服务器已启动\n'
    log_text.insert(tkinter.INSERT, log)
    while True:
        clientSocket, clientAddress = server.accept()
        username = get_username(clientSocket)
        userid_mapping[username] = clientSocket
        log = ('{}已经连接服务器\n'.format(username))
        log_text.insert(tkinter.INSERT, log)
        if username in MQ.keys():
            MQ_send_message(username, userid_mapping, MQ, log_text)
        t = Thread(target=rec_message, args=(userid_mapping, username, log_text, MQ), name='rec_message')
        t.start()


def start_server(server, log_text):
    userid_mapping = {}# 目标用户匹配
    MQ = {}# 消息存储
    s = Thread(target=start, args=(server, userid_mapping, MQ, log_text,), name='start_server')
    s.setDaemon(True)# 守护线程，和主线程同生同死
    s.start()


def end_server(server, win):
    server.close()
    win.quit()


def start_view():
    win = tkinter.Tk()
    win.title('Server')
    win.geometry('400x400+200+200')
    log_text = tkinter.Text(win)
    log_text.pack()
    server = socket(AF_INET, SOCK_STREAM)
    start_button = tkinter.Button(win, text='启动服务器', command=lambda: start_server(server, log_text))
    start_button.pack()
    end_button = tkinter.Button(win, text='退出', command=lambda: end_server(server, win))
    end_button.pack()
    win.mainloop()

if __name__ == '__main__':
    start_view()