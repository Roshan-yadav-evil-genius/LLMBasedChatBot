from Responder import StartResponder
from Listner import StartListner
from threading import Thread
import subprocess
import time
from view import StartChatServer
# Define the command to run
command = "python -m llama_cpp.server --model models/mistral-7b-instruct-v0.2.Q4_K_M.gguf --n_ctx 4000"

# Define the function to run the command
def run_command():
    subprocess.run(command, shell=True)

# Create a thread for running the command
command_thread = Thread(target=run_command)
command_thread.start()

time.sleep(20)
print("[+] Starting Responder")
responder_thread = Thread(target=StartResponder)
responder_thread.start()

ChatServer_thread = Thread(target=StartChatServer)
ChatServer_thread.start()
print("[+] Starting Listner")
StartListner()

# Continue with the rest of the code
responder_thread.join()
command_thread.join()
print("[+] Execution Completed")
