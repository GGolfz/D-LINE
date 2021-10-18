import time
from threading import Timer
from datetime import datetime
from multiprocessing import Process, Pipe
from os import getpid
class bcolors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    OKBLUE = '\033[94m'
    OKMAGENTA = '\033[95m'
    OKCYAN = '\033[96m'
    ENDC = '\033[0m'

def send_message(pipe,pid,vector_time,type,content,color):
    vector_time[0] += 1
    print(color+'Message send: '+ content + ' , ' + str(pid)+bcolors.ENDC)
    Timer(1 if type == 'text' else 5,pipe.send,[{'pid':pid,'content':content,'vector_time':vector_time.copy(),'type': type}]).start()
    return vector_time
def receive_message(pipe,pid,vector_time,buffer_list,color,is_process2=False,pipe23=None):
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
    print(color+'Message received: '+message['content'] +' , '+ str(pid)+bcolors.ENDC)
    if is_process2:
        vector_temp_send = send_message(pipe23,pid,vector_time[1].copy(),message['type'],message['content'],color)
        vector_temp = [vector_temp,vector_temp_send]
    n = len(buffer_list)
    for _ in range(n):
        vector_temp,buffer_list = handle_buffer_message(pid,vector_temp,buffer_list,buffer_list.pop(0),color,is_process2,pipe23)
    return vector_temp,buffer_list
def handle_buffer_message(pid,vector_time,buffer_list,message,color,is_process2,pipe23):
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
    print(color+'Message received: '+message['content'] +' , '+ str(pid)+bcolors.ENDC)
    if is_process2:
        vector_temp_send = send_message(pipe23,pid,vector_time[1].copy(),message['type'],message['content'],color)
        vector_temp = [vector_temp,vector_temp_send]
    return vector_temp,buffer_list
def process_one(pipe12,color):
    pid = getpid()
    vector_time = [0,0]
    buffer_list = []
    vector_time = send_message(pipe12,pid,vector_time,"text","text 1",color)
    vector_time = send_message(pipe12,pid,vector_time,"image","image 1",color)
    vector_time = send_message(pipe12,pid,vector_time,"text","text 2",color)
def process_two(pipe21,pipe23,color):
    pid = getpid()
    vector_time = [[0,0],[0,0]]
    buffer_list = []
    vector_time,buffer_list = receive_message(pipe21,pid,vector_time,buffer_list,color,True,pipe23)
    vector_time,buffer_list = receive_message(pipe21,pid,vector_time,buffer_list,color,True,pipe23)
    vector_time,buffer_list = receive_message(pipe21,pid,vector_time,buffer_list,color,True,pipe23)
def process_three(pipe32,color):
    pid = getpid()
    vector_time = [0,0]
    buffer_list = []
    vector_time,buffer_list = receive_message(pipe32,pid,vector_time,buffer_list,color)
    vector_time,buffer_list = receive_message(pipe32,pid,vector_time,buffer_list,color)
    vector_time,buffer_list = receive_message(pipe32,pid,vector_time,buffer_list,color)
def main():
    oneandtwo, twoandone = Pipe()
    twoandthree, threeandtwo = Pipe()

    process1 = Process(target=process_one, 
                       args=(oneandtwo,bcolors.OKBLUE))
    process2 = Process(target=process_two, 
                       args=(twoandone, twoandthree,bcolors.OKCYAN))
    process3 = Process(target=process_three, 
                       args=(threeandtwo,bcolors.OKGREEN))
    
    process1.start()
    process2.start()
    process3.start()

    process1.join()
    process2.join()
    process3.join()
    
if __name__ == '__main__':  
    main()