import time
from threading import Timer
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
class Process:
    def __init__(self,pid):
        self.pid = pid
        self.vector_time = {}
        self.buffer_list = []
        self.lock_buffer = False
        self.address = {pid:self}
        if pid == 1:
            self.color = bcolors.OKBLUE
        elif pid == 2:
            self.color = bcolors.OKCYAN
        elif pid == 3:
            self.color = bcolors.OKGREEN
    def connect(self,peer):
        print(str(self.pid) + " and " + str(peer.pid) + " are connected at time " + time.ctime() )
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
    def send_message_by_type(self,target,delay,type,content):
        self.vector_time[target.pid][self.pid] += 1
        print(self.color + str(self.pid) + " send the "+type+" message to "+ str(target.pid) + " at time "+ time.ctime() + '(sequence = '+ str(self.vector_time[target.pid][self.pid]) +')' + bcolors.ENDC)
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
                    # print("PUT HERE 2",self.pid, self.buffer_list,message)
                    self.buffer_list.append(message)
                    return False
        self.vector_time[message['pid']] = vector_temp
        print(self.color + str(self.pid) + " receive the "+ message['type'] + " message from " + str(message['pid'])+ " : " + message['content'] + " at time "+ time.ctime() +  '(sequence = '+ str(self.vector_time[message['pid']][message['pid']])  +')' + bcolors.ENDC)
        # If process 2 then forward to process 3
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
def main():
    p1 = Process(1)
    p2 = Process(2)
    p3 = Process(3)
    p1.connect(p2)
    p2.connect(p3)
    p1.send_message(p2,'text','text 1')
    p1.send_message(p2,'video','video 1')
    p1.send_message(p2,'image','image 1')
    p1.send_message(p2,'image','image 2')
    p1.send_message(p2,'text','text 2')
    p1.send_message(p2,'video','video 2')
    p2.send_message(p1,'video','video 1 from p2')
    p1.send_message(p2,'video','video 3')
    p1.send_message(p2,'text','text 3')
    p1.send_message(p2,'text','text 4')
    p1.send_message(p2,'image','image 3')
    p1.send_message(p2,'text','text 5')
    p1.send_message(p2,'text','text 6')
    p1.send_message(p2,'video','video 4')
    time.sleep(20)
    print(p1.buffer_list)
    print(p2.buffer_list)
    print(p3.buffer_list)
if __name__ == '__main__':  
    main()