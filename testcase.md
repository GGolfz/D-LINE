|Testcase No|Name|Description|Expected Output|Message List|
|---|---|---|---|---|
|1|One sender without buffer|In this test case, we want to simulation the message passing when we have only one sender. The receiver can receive the messages sequentially without buffering the early arrival messages, and it can forward those messages to another receiver with the same order of messages as received.|All people have the message in same order that the sender send|There are four messages sent from P1 which is our sender to P2. <br>1) Text Message with the content is "Hello Gobgab" <br>2) Text Message with the content is "Good Morning" <br>3) Text Message with the content is "How are you?"<br>4) Text Message with the content is "emoji"|
|2|One sender with only one message in buffer||||
|3|One sender with multiple messages in buffer||||
|4|Two senders with only one message in buffer||||
|5|Two senders with multiple messages in buffer||||