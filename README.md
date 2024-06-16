**SD_TASK1: ONLINE CHAT APPLICATION**

This project is a chat application built using Python, gRPC, and RabbitMQ. It provides various features, including private chats, persistent group chats, transient group chats, an insult channel and a discovery mechanism that allows users to find other available users and their different chat rooms.

RUNNING THE CHAT APPLICATION
1. Install all needed dependencies: pip install -r requirements.txt
2. Run 'start-server.sh' to initiate the server. To execute it: bin/bash ./start-server.sh
3. Run 'start-client.sh' as many clients you want. To execute it: /bin/bash ./start-client.sh name ip port
4. A menu will appear for every client initiated with all the different chat options.
5. You need to have RabbitMq installed and running to use some faetures. If you don't have it, execute the following script: /bin/bash ./rabbitmqscript.sh

FEATURES

•	PRIVATE CHATS: Users can engage in private conversations with other users.
•	GROUP CHATS: Users can participate in group chats which can be persistent or transient.
•	CHAT DISCOVERY: Users can discover all connected clients and obtain a list of all active chats.
•	INSULT CHANNEL: A dedicated channel where users can send and receive insults.

USAGE
1.	PRIVATE CHATS: To establish communication between two clients one of them must initiate the connection and then the other one connect to it.
2.	GROUP CHATS: The users must submit the group name and if it exists it connects to it and if it does not exist it creates it.
3.	CHAT DISCOVERY: Each user who wants to make their information available for discovery should choose the chat discovery response option and then the user who wants to discover other available clients and their chat rooms should initiate the discovery chat. To see all the responses the user has to stop the process by pressing Ctrl+C in each dedicated terminal.
4.	INSULT CHANNEL: Users who want to be insulted have to press the receive button to receive the insults while the users that want to send the insults must write them and press the send button. To see all the insults received the users have to stop the process by pressing Ctrl+C in each dedicated terminal.
