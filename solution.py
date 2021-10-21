import time
from threading import Timer
from datetime import datetime
import socket
class bcolors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    OKBLUE = '\033[94m'
    OKMAGENTA = '\033[95m'
    OKCYAN = '\033[96m'
    ENDC = '\033[0m'
class Process:
    def __init__(self,pid,pipe):
        self.pid = pid
        self.vector_time = {}
        self.buffer_list = []
        self.address = {pid:self}
        self.pipe = pipe
        if pid == 1:
            self.color = bcolors.OKBLUE
        elif pid == 2:
            self.color = bcolors.OKCYAN
        elif pid == 3:
            self.color = bcolors.OKGREEN
        else:
            self.color = bcolors.OKMAGENTA
    def connect(self,peer):
        log = bcolors.WARNING + datetime.now().strftime("%H:%M:%S") + " | " + str(self.pid) + " and " + str(peer.pid) + " are connected" + '\n'
        print(log,end='')
        self.address[peer.pid]=peer
        self.vector_time[peer.pid] = {self.pid: 0, peer.pid: 0}
        peer.address[self.pid] = self
        peer.vector_time[self.pid] = {self.pid: 0, peer.pid: 0}
    def send_message(self,target,type,content):
        if type == 'text':
            # text use 1s to sent
            self.send_message_by_type(target,1,type,content)
            if self.pid == 2 and target.pid == 1:
                self.send_message_by_type(self.address[3],1,type,content)
        elif type == 'image':
            # image use 3s to sent
            self.send_message_by_type(target,3,type,content)
            if self.pid == 2 and target.pid == 1:
                self.send_message_by_type(self.address[3],3,type,content)
        elif type == 'video':
            # video use 5s to sent
            self.send_message_by_type(target,5,type,content)
            if self.pid == 2 and target.pid == 1:
                self.send_message_by_type(self.address[3],5,type,content)
        time.sleep(0.5)
    def send_message_by_type(self,target,delay,type,content):
        self.vector_time[target.pid][self.pid] += 1
        log = self.get_send_log(target,content,type)
        print(log,end='')
        self.pipe.send(log.encode())
        message = {'pid':self.pid,'content':content,'vector_time':self.vector_time[target.pid].copy(),'type': type}
        Timer(delay,target.receive_message,[message]).start()
    def receive_message(self,message):
        vector_temp = self.vector_time[message['pid']].copy()
        vector_temp[message['pid']] += 1
        if vector_temp[message['pid']] != message['vector_time'][message['pid']]:
             # Push message that cannot receive now in to buffer list (Check 1 of causal ordering)
            if vector_temp[message['pid']] < message['vector_time'][message['pid']]:
                # print("PUT HERE 1",self.pid, self.buffer_list,message)
                self.buffer_list.append(message)
            return False
        for i in vector_temp.keys():
            if i != message['pid']:
                # Push message that cannot receive now in to buffer list (Check 2 of causal ordering)
                if message['vector_time'][i] > vector_temp[i]:
                    self.buffer_list.append(message)
                    return False
        self.vector_time[message['pid']] = vector_temp
        log = self.get_receive_log(message)
        print(log,end = '')
        self.pipe.send(log.encode())
        # If it is process 2 then forward to process 3
        if self.pid == 2:
            self.send_message(self.address[3],message['type'],message['content'])
        # Check message in buffer list
        if len(self.buffer_list) > 0:
            self.check_buffer_list(len(self.buffer_list))
        return True
    def check_buffer_list(self,round):
        for i in range(round):
            if len(self.buffer_list) == 0:
                break
            self.receive_message(self.buffer_list.pop(0))
    def get_send_log(self,target,content,type):
        return self.color + datetime.now().strftime("%H:%M:%S") + " | " + str(self.pid) + " send " + type + " message (" + content + ") to " + str(target.pid) + " (sequence time = " + str(self.vector_time[target.pid][self.pid]) + ")" + bcolors.ENDC + '\n'
    def get_receive_log(self,message):
        return self.color + datetime.now().strftime("%H:%M:%S") + " | " + str(self.pid) + " receive " + message['type'] + " message (" + message['content'] + ") from " + str(message['pid']) + " (sequence time = " + str(self.vector_time[message['pid']][message['pid']]) + ")" + bcolors.ENDC + '\n'
def main():
    socketp1 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    socketp1.connect(('localhost',5001))
    socketp2 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    socketp2.connect(('localhost',5002))
    socketp3 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    socketp3.connect(('localhost',5003))
    socketp4 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    socketp4.connect(('localhost',5004))
    p1 = Process(1,socketp1)
    p2 = Process(2,socketp2)
    p3 = Process(3,socketp3)
    p4 = Process(4,socketp4)
    p1.connect(p2)
    p1.connect(p4)
    p2.connect(p3)
    p2.connect(p4)
    p1.send_message(p2,'text','text 1')
    p1.send_message(p2,'video','video 1')
    p1.send_message(p2,'image','image 1')
    p1.send_message(p2,'image','image 2')
    p1.send_message(p4,'image','image 3')
    p1.send_message(p4,'image','image 4')
    p1.send_message(p2,'text','text 2')
    p1.send_message(p2,'video','video 2')
    p2.send_message(p1,'video','video 1 from p2')
    p1.send_message(p2,'video','video 3')
    p1.send_message(p2,'text','text 3')
    p1.send_message(p2,'text','text 4')
    p1.send_message(p2,'image','image 5')
    p1.send_message(p2,'text','text 5')
    p1.send_message(p2,'text','text 6')
    p1.send_message(p2,'video','video 4')
    p4.send_message(p1,'text','text 7')
    p4.send_message(p2,'text','text 8')
    time.sleep(20)
    print(p1.buffer_list)
    print(p2.buffer_list)
    print(p3.buffer_list)
    socketp1.close()
    socketp2.close()
    socketp3.close()
if __name__ == '__main__':  
    main()