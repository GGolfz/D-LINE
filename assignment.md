# CSC371 Introduction to Distributed Systems and Parallel Computing
## Assignment 1 (Group): Forwarding distributed LINE messages in the correct order

### Section 1: General overview of the library that you are using

We develop our simulation using Python with the built-in library such as time, datetime, threading, multiprocessing, os, and socket.

- `time` library provides us time related function, for this assignment we use `time.time()` to get the current timestamp and `time.sleep()` to delay between each message send.

- `threading` library provides us function about manage thread, for this assignment we use `threading.Timer` to send the message after specific time for simulating sending different kind of message.
