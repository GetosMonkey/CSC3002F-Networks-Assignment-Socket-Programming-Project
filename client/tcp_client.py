from socket import *
import threading

SERVER_HOST = "localhost"
SERVER_PORT = 12005

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect((SERVER_HOST, SERVER_PORT))
print("Connected to server.")
name = input("Enter chat username: ")
print("Type messages in chat!")


    


   # choice = show_menu()

   # authenticated = True

    #if choice =="1":
     #   authenticated = login(client_socket)
    #elif choice =="2":
    #    authenticated=sign_up(client_socket)
    ##else:
    #    print("Invalid Input!")

   # show_commands()

  

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            print(message)
            
   
        except:
            print("An error occurred!")
            client_socket.close()
            break

def send_messages(client_socket):
    while True:
        message = input()
        if message.lower() == "quit":
            client_socket.close()
            break
        message = name + ": " + message 
        client_socket.send(message.encode())
        

#def authenticate(username,password, client_socket):
    #message_string="Authenticate/"+username+"/"+password
   # client_socket.send(message_string.encode())



#def login(client_socket):
   # username = input("Enter username: ")
    #password = input("Enter password:  ")
    #authenticate(username,password,client_socket)
    #response= client_socket.recv(1024).decode)
    #if response ="SUCCESS":
    #    authenticated =True
    #else authenticated =False


    #return authenticated

#def show_commands():
   ### print("Select a command from the list below!") ## This method prompts the user to Login or sign-up
 #   print("1. Private Message") ## Login for existing users
  #  print("2. Message Group") ## sign-up for new users
   # print("3. Create New Group")
    #print("4. Join Group")
    


#def show_menu():
   # print("Welcome to ChatApp!") ## This method prompts the user to Login or sign-up
   ## print("1. Login") ## Login for existing users
  ##  print("2. Sign-up") ## sign-up for new users
  #  reply = input("Select option: ")
  #  return reply

 
#def sign_up(client_socket):
   # username=input("Enter a username: ")
    #password=input("Enter a password: ")
   ## message_string=input("NewUser"+"/"+username+"/"+password)
   ## client_socket.send(message_string.encode())
  #  return valid






threading.Thread(target= receive_messages, args=(client_socket,)).start()
threading.Thread(target= send_messages, args=(client_socket,)).start()