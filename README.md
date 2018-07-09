# Python Chat Server

This is simple client/server tcp connection that broadcasts messages to clients
that are connected to the server which runs on localhost. It uses ncurses right now to display the chat window.
There is login required. Users can be made using *starter_script.py*
>python -i startup_script.py


Running this open the python interpreter after the script is ran. This allows for easier creation of the database using sqlalchemy.

Once app.db is created run *server.py* and open a new terminal and run *ncurses_client.py.* to establish a connection. Then run another *ncurses_client.py* on another terminal to see the chat server broadcasting the messages.


#### Future Improvements
* User Registration
* Scrolling Window to see previous messages
* Encrypted messages
