from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route('/get_user_info', methods=['GET'])
def get_user_info():
    # The API endpoint 
    url = "https://mip-10741p.mpdv.cloud:8080/data/MDUser/list?X-Access-Id=00010741"

    # Username and password for basic authentication
    username = '12345'
    password = 'mpdv'

    # Request JSON data
    request_data = {
        "params": [{
            "acronym": "user.id",
            "value": ["5500", "5600"],
            "operator": "BETWEEN"
        }],
        "columns": ["user.designation", "user.id"],
        "requestId": 10,
        "returnAsObject": False
    }

    # Sending a POST request to the API with basic authentication and request data as JSON
    response = requests.post(url, json=request_data, auth=(username, password))

    # Check if the request was successful
    if response.status_code == 200:
        # Return the JSON response from the API
        return jsonify(response.json())
    else:
        # Return an error message if the request failed
        return jsonify({"error": "Failed to retrieve user information"}), 500

if __name__ == '__main__':
    app.run(debug=True)
