import os
from flask import Flask, request, jsonify
import time
import threading
import webbrowser
import subprocess
import socket
app = Flask(__name__)

base_url = 'https://mip-10741p.mpdv.cloud:50000/login?autoLoginClientId='
last_sleep_time = time.time()
theme = '&theme=mpdv-dark-theme'
previous_client_id = False

@app.route('/open-file', methods=['GET'])
def open_file():
    global last_sleep_time, previous_client_id
    client_id = request.args.get('number')
    if client_id:
        if client_id != previous_client_id:
            # Close Microsoft Edge browser
             os.system("taskkill /f /im msedge.exe") # To close current tabs in the following browsers
             os.system("taskkill /f /im chrome.exe")
             os.system("taskkill /f /im firefox.exe")
             os.system("taskkill /f /im opera.exe")
        
        # Wait for some time before opening the new URL (Optional)
        current_time = time.time()
        if current_time - last_sleep_time < 5 :  # Adjust the time interval as needed
            time.sleep(5)  # Wait for 5 seconds before opening the URL
        last_sleep_time = current_time

        if client_id != previous_client_id:
            url = base_url + client_id + theme
            webbrowser.open_new_tab(url)
            success = {"result": "success", "url": url}
            previous_client_id = client_id
            return jsonify(success), 200
        else:
            message = {"result": "Skipping, same client ID as before"}
            return jsonify(message), 200
    else:
        error = {"error": "Client ID is missing"}
        return jsonify(error), 400
def get_ip_address():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address


if __name__ == '__main__':
    app.run(debug=True, port=5000, host=get_ip_address())