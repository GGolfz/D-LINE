import time
from threading import Timer
class Process:
    def __init__(self,pid):
        self.pid = pid
        self.vector_time = {pid:0}
        self.buffer_list = []
        self.address = {pid:self}
    def connect(self,peer):
        print(str(self.pid) + " and " + str(peer.pid) + " are connected")
        self.address[peer.pid]=peer
        self.vector_time[peer.pid] = 0
        peer.address[self.pid] = self
        peer.vector_time[self.pid] = 0
    def send_message(self,target,type):
        if type == 'text':
            self.send_message_by_type(target,1,type)
        elif type == 'image':
            self.send_message_by_type(target,3,type)
        elif type == 'video':
            self.send_message_by_type(target,5,type)
    def send_message_by_type(self,target,time,type):
        self.vector_time[self.pid] += 1
        print(str(self.pid) + " send the "+type+" message to "+ str(target.pid))
        Timer(time,target.receive_message,[{'pid':self.pid,'content':'test '+ type,'vector_time':self.vector_time.copy(),'type': type}]).start()
    def receive_message(self,message):
        vector_temp = self.vector_time.copy()
        vector_temp[message['pid']] += 1
        if vector_temp[message['pid']] != message['vector_time'][message['pid']]:
            self.buffer_list.append(message)
            return False
        for i in vector_temp.keys():
            if i != message['pid']:
                if i in vector_temp and i in message['vector_time']:
                    if message['vector_time'][i] > self.vector_time[i]:
                        self.buffer_list.append(message)
                        return False
        self.vector_time = vector_temp
        print(str(self.pid) + " receive the text from " + str(message['pid'])+ " : " + message['content'])
        if self.pid == 2:
            self.send_message(self.address[3],message['type'])
        for i in self.buffer_list:
            self.buffer_list.remove(i)
            if self.receive_message(i) == False:
                self.buffer_list.append(i)
def main():
    p1 = Process(1)
    p2 = Process(2)
    p3 = Process(3)
    p1.connect(p2)
    p2.connect(p3)
    p1.send_message(p2,'image')
    p1.send_message(p2,'video')
    p1.send_message(p2,'text')
if __name__ == '__main__':
    main()