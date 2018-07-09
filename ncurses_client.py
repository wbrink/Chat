from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import socket
from threading import Thread

# the models that i made with sqlaclhemy
from model import Base, User
import pygame

import curses
import time
from curses.textpad import Textbox, rectangle

# custom sounds for chat
# contains variables with paths to sounds
import sounds



stdscr = curses.initscr()
curses.start_color()
curses.use_default_colors()
curses.init_pair(1, curses.COLOR_RED, -1)
curses.init_pair(2, curses.COLOR_GREEN, -1)
curses.init_pair(3, curses.COLOR_BLUE, -1)



class Client():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostname()
    port = 12345



    def __init__(self, username, editwin, displaywin, me_window):
        # initialize pygame mixer
        #player = pygame.mixer.init()

        self.username = username # byte string
        self.editwin = editwin
        self.box = Textbox(editwin)
        self.displaywin = displaywin
        self.displaywin.scrollok(True)
        self.me_window = me_window


        try:
            self.s.connect(("localhost", self.port))

        except socket.error: # catches the errors
            #print("socket connection failed. Try again")
            self.displaywin.addstr("Socket Connection Failed. Try again", curses.color_pair(1))
            self.displaywin.refresh()
            self.editwin.refresh()
            time.sleep(3)
            self.s.close()
            curses.endwin()
            sys.exit()


        #print("Welcome to the chat server")
        #sys.stdout.write("[Me :] \r"); sys.stdout.flush()
        self.displaywin.addstr("Welcome to the Chat Server {}! Press CTRL-C to exit\n".format(self.username), curses.color_pair(2))
        self.displaywin.refresh()
        self.editwin.refresh()
        #self.s.send(bytes(self.username, 'utf8'))
        self.s.send(self.username)


        # just to recieve greeting
        #data = self.s.recv(1024).decode('utf8')
        #sys.stdout.write(data)
        #print(data) # captures the welcome message

        sendingThread = Thread(target=self.send_messages)
        sendingThread.daemon = True
        sendingThread.start()

        while True: # want to constantly receive data
            data = self.s.recv(1024)
            if not data: # then the person has left
                break

            msg = data.decode('utf8')
            msg = msg + '\n' # add newline to end of the string

            #msg = self.add_color(msg)

            if "joined the chat" in msg and len(msg.split(':')) == 1:#if someone new enters the chat
                sound = 'open_door'
                play_thread = Thread(target=self.play_sound, args=(sound,))
                play_thread.daemon = True
                play_thread.start()
                #print(msg)
                #sys.stdout.write(msg)
                #sys.stdout.write("[Me :] \r"); sys.stdout.flush()
                self.displaywin.addstr(msg, curses.color_pair(3))
                self.displaywin.refresh()
                self.editwin.refresh()
            elif "left the chat" in msg and len(msg.split(':')) == 1: # someone lef the chat
                sound = 'close_door'
                play_thread = Thread(target=self.play_sound, args=(sound, ))
                play_thread.daemon = True
                play_thread.start()
                #sys.stdout.write(msg)
                #sys.stdout.write("[Me :] \r"); sys.stdout.flush()
                self.displaywin.addstr(msg, curses.color_pair(3))
                self.displaywin.refresh()
                self.editwin.refresh()
            elif self.username.decode() == msg[:len(self.username.decode())]: # then message was sent
                # sound is managed in the sending thread

                username, *msg = msg.split(':') # the first on will be the username will get red name
                message = ':'.join(msg)
                username = username + ':'

                self.displaywin.addstr(username, curses.color_pair(1))
                self.displaywin.addstr(message)
                self.displaywin.refresh()
                self.editwin.refresh()
            else: # just a regular message recieved
                sound = 'message_received'
                play_thread = Thread(target=self.play_sound, args=(sound, ))
                play_thread.daemon = True
                play_thread.start()

                username, *msg = msg.split(':') # the first on will be the username will get red name
                message = ':'.join(msg)
                username = username + ':'

                self.displaywin.addstr(username, curses.color_pair(3)) # blue
                self.displaywin.addstr(message)
                self.displaywin.refresh()
                self.editwin.refresh()
                #sys.stdout.write("[Me :] \r"); sys.stdout.flush()

# once message comes in it should overwrite what is not entered, then


    def send_messages(self):
        while True:
            # resets color \033[0;0m
            #msg = input("\033[92m") green color
            #msg = msg + "\033[0m" back to normal
            #msg = sys.stdin.readline()

            self.box.edit(self.enter_is_terminate) # enter is terminate makes enter terminate the script rather than ctrl-g
            # Get resulting contents (should block)
            message = self.box.gather()

            # if message keeps going
            if '\n' in message:
                message = message.replace('\n', '')

            self.editwin.clear()
            self.editwin.refresh()
            message = "{}: {}".format(self.username.decode(), message)
            message = bytes(message, 'utf8')
            self.s.send(message)

            # for playing the sound
            sound = 'message_sent'
            play_thread = Thread(target=self.play_sound, args=(sound, ))
            play_thread.daemon = True
            play_thread.start()


    # sounds.py contains variables where the sounds are stored
    def play_sound(self, sound):
        pygame.mixer.init()

        if sound == 'open_door':
            pygame.mixer.music.load(sounds.entered) # paths located in sounds.py
        elif sound == 'close_door':
            pygame.mixer.music.load(sounds.exited)
        elif sound == 'message_received':
            pygame.mixer.music.load(sounds.recieved)
        elif sound == 'message_sent':
            pygame.mixer.music.load(sounds.sent)

        pygame.mixer.music.play()

    # validator made for box.edit()
    # this makes enter act like ctrl-g which is how to return and exit
    def enter_is_terminate(self,x):
        if x == 10:
            return 7
        else:
            return x


# ================ ascii escapes don't work with ncurses ==========================
    """
    def add_color(self, msg):
        if len(msg.split(':')) == 1: # then message from server saying someone joined or left
            msg = "\033[34;1m" + msg + "\033[0m"
            return msg
        else: # then message from me or other user
            message = msg.split(':') # the first on will be the username will get red name
            if message[0] = self.username.decode(): # then user is me
                message[0] = "\033[31;1m" + message[0] + "\033[0m"
                msg = ':'.join(message)
                return msg
            else: # some other user which will get blue name
                message[0] = "\033[34;1m" + message[0] + "\033[0m"
                msg = ':'.join(message)
                return msg
    """





def login(stdscr):
    #curses.use_default_colors()
    stdscr.clear()
    curses.echo()
    stdscr.addstr('Are you a registered user? Y/N?\n')
    stdscr.refresh()
    response = stdscr.getstr() # stored as byte code
    if response in [b'Y', b'y']:
        stdscr.addstr("User: ")
        username = response = stdscr.getstr() # stored as bytes i.e (b'string')
        #stdscr.addstr("{}\n".format(username.decode()))
        stdscr.addstr("Password: ")
        curses.noecho() # don't want to be able to see password
        password = stdscr.getstr()
        #stdscr.addstr(password)
        stdscr.refresh()

    # ================Database code=================================
        # using the created database
        engine = create_engine('sqlite:///app.db')
        # bind the negine to the metadat of the base class so tthat the delcaratives
        # can be accessed through a DBSession instance
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        user = session.query(User).filter(User.username == username.decode()).first()
        if user: # if the username is correct
            # since all usernames must be unique
            if user.check_password(password.decode()): # username exists, checks password
                #curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
                stdscr.addstr("Access Granted", curses.color_pair(2))
                stdscr.refresh()
                time.sleep(2)

                # calls the chat application fucntion()
                return username # scucess


            else:
                stdscr.addstr("Login Failed")
                stdscr.refresh()
                time.sleep(3)
        else:
            stdscr.addstr("Login Failed")
            stdscr.refresh()
            time.sleep(3)


    else:
        stdscr.addstr("You may not enter the chat")
        stdscr.refresh()
        time.sleep(3)


def chat(stdscr, username):
    stdscr.clear()
    #curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.use_default_colors()
    stdscr.scrollok(True)

# =============making the edit box for the bottom of the screen===========
    #height, width, begin_y, begin_x
    # assumeing an 80x24 terminal
    editwin = curses.newwin(3,75, 20,5)
    #box = Textbox(editwin)


# ============= window for displaying the messages =================
    displaywin = curses.newwin(19, 80, 0,0)
    displaywin.scrollok(True)
    #displaywin.addstr("Welcome to the messenger")
    displaywin.refresh()


#============= Make window for the instrction ========================
    me_window = curses.newwin(1,5, 20,0)
    me_window.addstr("Me :")
    #me_window.box()
    me_window.refresh()


#============= main loop ===========================

    chat_client = Client(username, editwin, displaywin, me_window)




if __name__ == '__main__':
    username = curses.wrapper(login)

    # login returns username on sucesss
    if username: #then login was successful
        print('login success')
        # calls the chat application fucntion()
        curses.wrapper(chat, username)
    else: # no login
        print("didn't go well")

    curses.endwin()
