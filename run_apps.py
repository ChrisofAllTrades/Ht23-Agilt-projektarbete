import subprocess
import time
import requests
import signal

def check_flask_app():
    try:
        response = requests.get('http://127.0.0.1:5000')
        return response.status_code == 200
    except requests.ConnectionError:
        return False

def terminate_processes(*processes):
    for p in processes:
        p.terminate()
        p.wait()

def signal_handler(sig, frame):
    print('Terminating processes...')
    terminate_processes(flask_process, streamlit_process)
    exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Start the Flask app
flask_process = subprocess.Popen(['python', 'flask_app.py']) #Skapa denna fil för att köra flask.

# Wait for the Flask app to be up and running
while not check_flask_app():
    time.sleep(1)

# Start the Streamlit app
streamlit_process = subprocess.Popen(['streamlit', 'run', 'streamlit-app.py'])
