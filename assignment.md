# CSC371 Introduction to Distributed Systems and Parallel Computing
## Assignment 1 (Group): Forwarding distributed LINE messages in the correct order

### Member

62130500206 Kaewket Saelee

62130500226 Wisarut Kitticharoenphonngam

62130500254 Kavisara Srisuwatcharee

### Requirement
D-Line wants to maintain the correct order of the messages from the sender regardless of when the messages actually arrive at the destination.

### Theoretical discussion of solution

From the requirement, we originate with the idea that we can use causal ordering to order the message in each receiver. But the problem is if we have P1, P2, and P3 while P1 and P2 communicate together and P2 will forward messages to P3 that means P1 and P3 shouldn't able to communicate. So we decide to create two groups of communication. The first is P1 and P2 and the second is P2 and P3. Each group will maintain the order of the message using causal ordering.

### System Architecture

Since we decide to have 3 people P1, P2, and P3 where P1 can send and receive messages from P2, P2 can send messages to P1 and P3 but can receive messages from P1, and P3 can receive messages from P2, the system architecture of communication between each people is shown as below.

<!-- แปะรูป System Arch.jpeg -->

### Implementation

We start with searching for a pre-defined library about causal ordering. Unfortunately, we didn't find the meet our needs so we decide to develop the solution by own. 

We decide to develop our simulation using Python with a built-in library such as datetime, multiprocessing, os, socket, time, and threading.

- `datetime` library provides us a function that can manipulate date and time, for this assignment we use `datetime.now()` to get the current time and `datetime.strftime()` to format time in the format that we want.

- `multiprocessing` library helps us to manipulate about subprocess in concurrent and allow us to send the data between each process, for this assignment it is the main library that we use to send the message from one process to another process. We use `Process` to simulate a user, `Pipe` as the communication way between people, and `Array` for store shared state.

- `os` library allows us to access the id of the process in the system, we use `getpid()` to get the process id of the current process.

- `socket` library allows us to transfer data across the network to display in another terminal that we use Netcat to open port for communication.

- `time` library provides us with time-related functions, for this assignment we use `time.sleep()` to delay between each message sent.

- `threading` library provides us function about managing thread, for this assignment we use `threading.Timer` to send the message after a specific time for simulating sending a different kinds of message.

Let start with the definition before starting implementation.

The delay are 0.5 seconds for sending messages and 0 seconds for forwarding a message. 

There are 3 types of messages.

1) Text Message uses 1 second for delivery.

2) Image Message uses 3 seconds for delivery.

3) Video Message uses 5 seconds for delivery.

Next is the explanation of how our source code come up.

Since we want to use causal ordering which two groups of communication so each people will have its buffer_list and its vector_time to each group. But in the second group, there is only one sender which is P2 so it doesn't need to have buffer_list for that group because it always sends the messages.

P1 will have vector_time and a buffer list of communication with P2.

P2 will have vector_time and a buffer list of communication with P1, and vector_time of communication with P3.

P3 will have vector_time and a buffer list of communication with P2.

We start implementation by using objects for representing the people as you can see in `solution.py`. In this file, `Process` class has buffer_list as `List` to store the message that buffered and vector_time as `Dict` that we decide to make it 2D Dict first dimension is the target group and the second dimension is vector_time in each group. There are four significant methods of `Process` object are `send_message`, `send_message_by_type`, `receive_message`, `check_buffer_list`.

1) `send_message` is the method that we create for setting the delay of each type of message and we also check that if the sender is P2 it also send to P3.

2) `send_message_by_type` is the method that we implement same as the causal ordering concept that we add the vector time of the sender by 1 and send the message to other people.

3) `receive_message` is the method that we implement same as the causal ordering concept that when we receive the message we need to check two conditions. First is vector time of sender from incoming message must equal our vector time of sender that we plus 1. Second is other vector time of receiver must more than or equal the vector time of sender. Otherwise, the message will be buffered and stored in a buffer list.

4) `check_buffer_list` is the method that we use for checking that we can receive the message in the buffer list or not that we will call when receiving message success.

The code is run in sequence in a single process, works as our expectation, and sent the output to show in another 3 terminal using `socket` and `netcat`. 

Then we change from use object to use process for representing the people. We bring `multiprocessing` library in our project for implementation. The code is in `solution_multithread.py`. The code is similar to before, it just changes the method name and refactors to be implemented in multi-process. Now the flow of our solution is changed since when wait to receive a message from another process the process cannot send the message or do anything else. But we think it is acceptable since in the real world when we communicate with people if we talk about the same topic we need to know the message of other people before we reply. 

### Testcase

<!-- เอาของชิงมาใส่ -->

### Simulation Result

<!-- เอาของอปมาใส่ -->

### User Manual
<!-- ถ้าว่างอาจจะนั่งแคปรูปแต่ละ step มาแปะให้หน่อยก็ดี :) -->
1) Open 4 terminals
2) Run 1st terminal using `nc -l 5001`
3) Run 2nd terminal using `nc -l 5002`
4) Run 3rd terminal using `nc -l 5003`
5) Run `python3 concept_multithread.py` in the last terminal or `python3 concept_multithread.py < testcase-n.in` (n is from 1 to 5) if you want to use a predefined test case.
6) Configure port of process#1 to be `5001`
7) Configure port of process#2 to be `5002`
8) Configure port of process#3 to be `5003`
9) Select type of messages (text, image, video)
10) Select sender (1 or 2)
11) Type the message content
12) Repeat steps 9-11 until you want to stop (press 0 for stop)
13) The simulation will show in all terminals.