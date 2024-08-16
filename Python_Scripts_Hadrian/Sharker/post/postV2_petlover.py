import os
from flask import Flask, request, jsonify
import time
import threading
import webbrowser
import socket
import wakeonlan

x_time = 18 # time that the pc will go to sleep in 24 hour format
y_time = 2 * 2600  # # time that pc will go to sleep after waking up in seconds
reset_hour = 8
app = Flask(__name__)
filename = 'file:///C:/Users/C4AI/Desktop/demo.html' # can be replaced with any link/file directory
last_sleep_time = time.time()
sleeping = False  # Flag to track if the computer is sleeping

@app.route('/', methods=['POST', 'GET'])
def result():
    if request.method == 'POST':
        print(request.form['name'])  # should display 'bar'
    else:
        print("get")
        user = request.args.get('accessRecordId')
    success = {"result": "success"}
    webbrowser.open_new_tab(filename)
    return jsonify(success), 200

def sleep_after():
    global last_sleep_time, sleeping
    while True:
        current_time = time.localtime()

        # Check if the current time is past 18:00 and the PC is on
        if current_time.tm_hour >= x_time and not sleeping:
            # Put the computer to sleep
            print("Putting computer to sleep as it's past 18:00...")
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            last_sleep_time = time.time()  # Update last sleep time
            sleeping = True  # Set sleeping flag to True to indicate the computer is sleeping
            time.sleep(60)  # Sleep for a minute to avoid multiple sleep calls

        elif time.time() - last_sleep_time >= y_time + 60 and sleeping:  # Reset the sleeping flag after 2 hours and 1 minute
            print("Resetting sleeping flag after 2 hours and 1 minute of being asleep...")
            sleeping = False  # Reset the sleeping flag to indicate the computer is awake
            last_sleep_time = time.time()  # Update last sleep time
            time.sleep(60)  # Sleep for a minute to avoid multiple calls

        elif time.time() - last_sleep_time >= y_time and not sleeping:  # Check if it's been 2 hours since last sleep
            print("Putting computer to sleep after 2 hours of being awake...")
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            last_sleep_time = time.time()  # Update last sleep time
            sleeping = True  # Set sleeping flag to True to indicate the computer is sleeping
            time.sleep(60)  # Sleep for a minute to avoid multiple sleep calls

        elif sleeping and current_time.tm_hour == reset_hour:  # Reset at specified hour
            print("Resetting sleep flag at specified hour...")
            sleeping = False  # Reset the sleeping flag to indicate the computer is awake
            last_sleep_time = time.time()  # Reset the last sleep time

        else:
            time.sleep(60)  # Check every minute

@app.route('/sleep', methods=['POST'])
def go_to_sleep():
    data = request.get_json()
    if data and data.get("command") == "sleep":
        print("Received sleep command. Putting the computer to sleep.")
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        return {"result": "going to sleep"}, 200
    return {"error": "Invalid command"}, 400

@app.route('/wakeup', methods=['POST'])
def wake_up():
    global sleeping
    if sleeping:
        print("Waking up the computer...")
        # You can add any actions needed to wake up the computer here
        sleeping = False  # Reset the sleeping flag to indicate the computer is awake
        return {"result": "Computer woken up successfully"}, 200
    else:
        return {"error": "Computer is not sleeping"}, 400
def get_ip_address():
    hostname = socket.gethostname()
    own_ip_address = socket.gethostbyname(hostname)
    return own_ip_address

if __name__ == '__main__':
    # Start the sleep_after function in a separate thread
    sleep_thread = threading.Thread(target=sleep_after)
    sleep_thread.start()
    
    # Start Flask app
    app.run(debug=True, port=5000, host= get_ip_address())