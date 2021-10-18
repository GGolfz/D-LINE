import time
from threading import Timer
from datetime import datetime
from multiprocessing import Process, Pipe, Array
from os import getpid
import socket

class bcolors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    OKBLUE = '\033[94m'
    OKMAGENTA = '\033[95m'
    OKCYAN = '\033[96m'
    ENDC = '\033[0m'

def get_send_log(color,source,target,vector_time,content,type):
    return color + datetime.now().strftime("%H:%M:%S") + " | " + str(source) + " send " + type + " message (" + content + ") to " + str(target) +" (sequence time = " + str(vector_time) + ")" + bcolors.ENDC + '\n'

def get_receive_log(color,source,vector_time,message):
    return color + datetime.now().strftime("%H:%M:%S") + " | " + str(source) + " receive " + message['type'] + " message (" + message['content'] + ") from " + str(message['pid']) + " (sequence time = " + str(vector_time) + ")" + bcolors.ENDC + '\n'

def send_message(pipe,pid,target,vector_time,type,content,color,socket,pid_list,delay=0):
    vector_time[0] += 1
    log = get_send_log(color,pid,pid_list[target-1],vector_time[0],content,type)
    print(log,end='')
    socket.send(log.encode())
    sec = 1
    if type == 'text':
        sec = 1
    elif type == 'image':
        sec = 3
    elif type == 'video':
        sec = 5
    Timer(sec,pipe.send,[{'pid':pid,'content':content,'vector_time':vector_time.copy(),'type': type}]).start()
    time.sleep(delay)
    return vector_time

def receive_message(pipe,pid,vector_time,buffer_list,color,socket,pid_list,is_process2=False,pipe23=None):
    message = pipe.recv()
    vector_temp = vector_time.copy()
    if is_process2:
        vector_temp = vector_time[0].copy()
    vector_temp[1] += 1
    if vector_temp[1] < message['vector_time'][0]:
        buffer_list.append(message)
        return vector_time,buffer_list
    if vector_temp[0] < message['vector_time'][1]:
        buffer_list.append(message)
        return vector_time,buffer_list
    log = get_receive_log(color,pid,vector_temp[1],message)
    print(log,end='')
    socket.send(log.encode())
    if is_process2:
        vector_temp_send = send_message(pipe23,pid,3,vector_time[1].copy(),message['type'],message['content'],color,socket,pid_list)
        vector_temp = [vector_temp,vector_temp_send]
    n = len(buffer_list)
    for _ in range(n):
        if len(buffer_list) == 0:
            break
        vector_temp,buffer_list = handle_buffer_message(pid,vector_temp,buffer_list,buffer_list.pop(0),color,socket,pid_list,is_process2,pipe23)
    return vector_temp,buffer_list

def handle_buffer_message(pid,vector_time,buffer_list,message,color,socket,pid_list,is_process2,pipe23):
    vector_temp = vector_time.copy()
    if is_process2:
        vector_temp = vector_time[0].copy()
    vector_temp[1] += 1
    if vector_temp[1] < message['vector_time'][0]:
        buffer_list.append(message)
        return vector_time,buffer_list
    if vector_temp[0] < message['vector_time'][1]:
        buffer_list.append(message)
        return vector_time,buffer_list
    log = get_receive_log(color,pid,vector_temp[1],message)
    print(log,end='')
    socket.send(log.encode())
    if is_process2:
        vector_temp_send = send_message(pipe23,pid,3,vector_time[1].copy(),message['type'],message['content'],color,socket,pid_list)
        vector_temp = [vector_temp,vector_temp_send]
    n = len(buffer_list)
    for _ in range(n):
        if len(buffer_list) == 0:
            break
        vector_temp,buffer_list = handle_buffer_message(pid,vector_temp,buffer_list,buffer_list.pop(0),color,socket,pid_list,is_process2,pipe23)
    return vector_temp,buffer_list

def process_one(msg_list,pipe12,color,socket,pid_list):
    pid = getpid()
    vector_time = [0,0]
    buffer_list = []
    for i in msg_list:
        vector_time = send_message(pipe12,pid,2,vector_time,i[0],i[1],color,socket,pid_list,i[2])

def process_two(msg_list,pipe21,pipe23,color,socket,pid_list):
    pid = getpid()
    vector_time = [[0,0],[0,0]]
    buffer_list = []
    for _ in msg_list:
        vector_time,buffer_list = receive_message(pipe21,pid,vector_time,buffer_list,color,socket,pid_list,True,pipe23)

def process_three(msg_list,pipe32,color,socket,pid_list):
    pid = getpid()
    vector_time = [0,0]
    buffer_list = []
    for _ in msg_list:
        vector_time,buffer_list = receive_message(pipe32,pid,vector_time,buffer_list,color,socket,pid_list)

def main():
    port_list = [5001,5002,5003]
    for i in range(len(port_list)):
        port_list[i] = int(input("Please Specify PORT for process#"+str(i+1)+": "))
    
    type = 1
    msg_list = []
    ts = time.time()
    while(type != "0"):
        type = input("Choose Message Type (text,image,video) or 0 for end: ")
        if type == '0':
            break
        message = input("Input Message Name: ")
        te = time.time()
        msg_list.append((type,message,te-ts))
        ts = te

    oneandtwo, twoandone = Pipe()
    twoandthree, threeandtwo = Pipe()
    
    socketp1 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    socketp1.connect(('localhost',port_list[0]))
    socketp2 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    socketp2.connect(('localhost',port_list[1]))
    socketp3 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    socketp3.connect(('localhost',port_list[2]))
    pid_list = Array('i',[0,0,0])
    process1 = Process(target=process_one, 
                       args=(msg_list,oneandtwo,bcolors.OKBLUE,socketp1,pid_list))
    process2 = Process(target=process_two, 
                       args=(msg_list,twoandone, twoandthree,bcolors.OKCYAN,socketp2,pid_list))
    process3 = Process(target=process_three, 
                       args=(msg_list,threeandtwo,bcolors.OKGREEN,socketp3,pid_list))
    process1.start()
    process2.start()
    process3.start()

    pid_list[0] = process1.pid
    pid_list[1] = process2.pid
    pid_list[2] = process3.pid
    
    process1.join()
    process2.join()
    process3.join()
    
if __name__ == '__main__':  
    main()