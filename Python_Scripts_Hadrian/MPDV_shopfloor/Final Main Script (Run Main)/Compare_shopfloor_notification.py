import requests
import json
import time
import subprocess
import re
import socket
from dotenv import load_dotenv

# libraries for email notification feature
import os
from mailjet_rest import Client as MailjetClient


# libraries for sms notification feature
from twilio.rest import Client as TwilioClient
from twilio.base.exceptions import TwilioRestException


# Load environment variables from .env file
load_dotenv()

# Email account for testing
EMAIL_USER = os.getenv("EMAIL_USER")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_NAME = os.getenv("SENDER_NAME")

# Twilio configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
YOUR_PHONE_NUMBER = os.getenv("YOUR_PHONE_NUMBER")

# Notification recipients for another feature, which is email notifications
RECIPIENTS = EMAIL_USER

# Initialize Twilio client for sms
twilio_client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Mailjet Configuration
MAILJET_API_KEY = os.getenv("MAILJET_API_KEY")
MAILJET_SECRET_KEY = os.getenv("MAILJET_SECRET_KEY")

if not MAILJET_API_KEY or not MAILJET_SECRET_KEY:
    raise ValueError("Mailjet API credentials are not set in the environment variables.")

mailjet_client = MailjetClient(auth=(MAILJET_API_KEY, MAILJET_SECRET_KEY))

# FaceSec API endpoints, PLEASE CHANGE IP in the links below to match FaceSec IP
FACESEC_LOGIN_URL = "http://172.17.170.96:8081/api/account/login?password=25802580"
FACESEC_PERSONS_URL = "http://172.17.170.96:8081/api/persons?size=100&page=0"
FACESEC_RULES_URL = "http://172.17.170.96:8081/api/rules"
FACESEC_ADD_PERSONNEL_URL = "http://172.17.170.96:8081/api/person"
FACESEC_UPLOAD_IMAGE_URL = "http://172.17.170.96:8081/api/upload/image"

# Added FaceSec API endpoints, uses the same IP as the rest of the endpoints
FACESEC_LOGOUT_URL = "http://172.17.170.96:8081/api/account/logout"

# Check if all necessary environment variables are set
if not all([MAILJET_API_KEY, MAILJET_SECRET_KEY, SENDER_EMAIL, SENDER_NAME, RECIPIENTS]):
    raise ValueError("One or more Mailjet environment variables are missing.")

# HYDRA API endpoint
HYDRA_URL = "https://mip-10741p.mpdv.cloud:8080/data/BOPerson/list?X-Access-Id=00010741"

# Global variables to store uploaded image data and rule ID
uploaded_image_data = None
rule_id = None

# Added functions
# Getting Twilio Phone Number for Phone Notification System
def get_twilio_phone_number():
    try:
        phone_numbers = twilio_client.incoming_phone_numbers.list()
        for number in phone_numbers:
            capabilities = number.capabilities
            if capabilities.get('sms'):
                return number.phone_number
        raise Exception("No valid Twilio phone numbers available for sending SMS.")
    except Exception as e:
        print(f"Failed to retrieve Twilio phone number. Error: {str(e)}")
        return None

# Logout function
def logout_to_facesec(cookies):
    try:
        response = requests.get(FACESEC_LOGOUT_URL, cookies=cookies)
        if response.status_code == 200:
            print("Logged out Successfully!")
        else:
            print(f"Failed to logout. Status code: {response.status_code}, Response: {response.text}")
    except requests.RequestException as e:
        print(f"Error logging out from FaceSec API: {e}")

    return response 

# Email Notification    
def send_email(subject, body, sender_email, sender_name, to_email):
    data = {
        'Messages': [
            {
                'From': {
                    'Email': sender_email,
                    'Name': sender_name
                },
                'To': [
                    {
                        'Email': to_email,
                        'Name': 'Recipient'
                    }
                ],
                'Subject': subject,
                'TextPart': body
            }
        ]
    }
    try:
        result = mailjet_client.send.create(data=data)
        if result.status_code == 200:
            print("Email sent successfully.")
        else:
            print("Failed to send email. Response:", result.json())
    except Exception as e:
        print(f"Failed to send email. Error: {str(e)}")


# SMS Notification function
def send_sms(to_number, message):
    from_number = get_twilio_phone_number()
    if not from_number:
        print("No Twilio phone number available to send SMS.")
        return
    
    try:
        message = twilio_client.messages.create(
            body=message,
            from_=from_number,
            to=to_number
        )
        print(f"Message sent successfully. SID: {message.sid}")
    except TwilioRestException as e:
        print(f"Failed to send message. Error: {e.msg}")
        return None


# End of implemented functions

async def login_to_facesec():
    try:
        response = requests.get(FACESEC_LOGIN_URL)
        if response.status_code == 200:
            print("Successfully logged in to FaceSec API")
            return response.cookies
        else:
            print(f"Failed to login. Status code: {response.status_code}, Response: {response.text}")
    except requests.RequestException as e:
        print(f"Error logging into FaceSec API: {e}")

    print("Failed to login to FaceSec API")
    return None

async def access_personnel_list(cookies):
    try:
        response = requests.get(FACESEC_PERSONS_URL, cookies=cookies)
        if response.status_code == 200:
            print("Successfully accessed personnel list:")
            personnel_data = response.json()
            pretty_printed_data = json.dumps(personnel_data, indent=4)
            print(pretty_printed_data)
            return personnel_data
        else:
            print(f"Failed to access personnel list. Status code: {response.status_code}, Response: {response.text}")
    except requests.RequestException as e:
        print(f"Error accessing personnel list: {e}")

    print("Failed to access personnel list")
    return None

async def retrieve_identification_rules(cookies):
    global rule_id

    try:
        response = requests.get(FACESEC_RULES_URL, cookies=cookies)
        if response.status_code == 200:
            print("Successfully accessed identification rules:")
            rules_data = response.json()
            print("Raw rules data:", rules_data)

            if isinstance(rules_data, dict) and 'entity' in rules_data:
                rules = rules_data['entity']
            else:
                print("Unexpected data structure for rules:", type(rules_data))
                return False

            if isinstance(rules, list) and rules:
                rules_info = [{'id': rule['id'], 'name': rule['name']} for rule in rules]
                pretty_printed_rules = json.dumps(rules_info, indent=4)
                print(pretty_printed_rules)

                rule_id = rules_info[0]['id']
                return True
            else:
                print("Unexpected data structure for rules:", type(rules))
        else:
            print(f"Failed to access rules. Status code: {response.status_code}, Response: {response.text}")
    except requests.RequestException as e:
        print(f"Error accessing identification rules: {e}")

    print("Failed to access identification rules")
    return False

async def upload_image(image_file_path, upload_url, cookies):
    global uploaded_image_data
    
    if uploaded_image_data:
        print("Image already uploaded. Reusing existing imagePath:", uploaded_image_data.get("imagePath", ""))
        return uploaded_image_data
    
    try:
        with open(image_file_path, 'rb') as file:
            files = {'file': (image_file_path, file, 'image/jpeg')}
            response = requests.post(upload_url, files=files, cookies=cookies)
            if response.status_code == 200:
                uploaded_image_data = response.json()
                print("Image uploaded successfully")
                return uploaded_image_data
            else:
                print(f"Failed to upload image. Status code: {response.status_code}, Response: {response.text}")
    except FileNotFoundError:
        print(f"File not found: {image_file_path}")
    except requests.RequestException as e:
        print(f"Error uploading image: {e}")
    return None

async def add_personnel_to_facesec(personnel_data, cookies):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    try:
        response = requests.post(FACESEC_ADD_PERSONNEL_URL, json=personnel_data, cookies=cookies, headers=headers)
        if response.status_code == 200:
            print("Personnel added successfully to FaceSec")
            return True
        else:
            print(f"Failed to add personnel to FaceSec. Status code: {response.status_code}")
            print("Response:", response.json())
    except requests.RequestException as e:
        print(f"Error adding personnel to FaceSec: {e}")
    return False

async def get_user_info_from_hydra():
    username = '12345'
    password = 'mpdv'
    request_data = {
        "params": [{
            "acronym": "person.card_id",
            "value": ["5500", "5600"],
            "operator": "BETWEEN"
        }],
        "columns": ["person.card_id", "person.name"],
        "requestId": 14,
        "returnAsObject": False
    }
    try:
        response = requests.post(HYDRA_URL, json=request_data, auth=(username, password))
        if response.status_code == 200:
            print("Successfully retrieved user information from HYDRA")
            return response.json()
    except requests.RequestException as e:
        print(f"Error retrieving user information from HYDRA: {e}")
    print("Failed to retrieve user information from HYDRA")
    return None

async def compare_data(facesec_data, hydra_data):
    facesec_dict = {(entry['name'], entry['no']) for entry in facesec_data['entity']['content']}
    hydra_dict = {(entry['data'][1], entry['data'][0]) for entry in hydra_data[1:]}

    matching_users = facesec_dict.intersection(hydra_dict)
    non_matching_hydra = hydra_dict - facesec_dict

    comparison_result = {
        "matching_users": [
            {"name": name, "no": no}
            for name, no in matching_users
        ],
        "non_matching_hydra": [
            {"name": name, "no": no}
            for name, no in non_matching_hydra
        ]
    }

    return comparison_result

def compare_and_sync():
    cookies = login_to_facesec()
    if cookies:
        try:
            # Access FaceSec data
            facesec_data = access_personnel_list(cookies)
            if facesec_data:
                # Extract personnel data from FaceSec
                facesec_personnel = facesec_data.get('entity', {}).get('content', [])
                
                # Access Hydra data
                hydra_data = get_user_info_from_hydra()
                if hydra_data:
                    # Extract user data from Hydra
                    hydra_users = [item['data'] for item in hydra_data if item['__rowType'] == 'DATA']
                    
                    # Compare data
                    comparison_result = compare_data(facesec_personnel, hydra_users)
                    pretty_printed_result = json.dumps(comparison_result, indent=4)
                    print(pretty_printed_result)

                    # Retrieve rule ID
                    if retrieve_identification_rules(cookies):
                        print("Retrieved rule ID:", rule_id)

                        # Upload image
                        image_file_path = "C:/Users/Hadrian Yeo/Documents/Images/face.jpg"  # Change this file path as needed
                        uploaded_image_data = upload_image(image_file_path, FACESEC_UPLOAD_IMAGE_URL, cookies)
                        if uploaded_image_data:
                            print("Uploaded image data:", uploaded_image_data)

                            image_path = uploaded_image_data.get("entity", "")
                            if image_path:
                                print("Image path:", image_path)

                                # Process non-matching users
                                for person in comparison_result["non_matching_hydra"]:
                                    personnel_data = {
                                        "name": person["name"],
                                        "no": person["no"],
                                        "idCard": "",
                                        "ruleId": rule_id,
                                        "icNumber": "",
                                        "wgNumber": "",
                                        "groupId": "",
                                        "imagePath": image_path
                                    }

                                    print("Personnel data being sent:", json.dumps(personnel_data, indent=4))

                                    if add_personnel_to_facesec(personnel_data, cookies):
                                        print(f"Personnel {person['name']} added successfully!")
                                    else:
                                        error_message = f"Failed to add personnel {person['name']}."
                                        print(error_message)
                                        send_sms(YOUR_PHONE_NUMBER, error_message)
                                        send_email(
                                            subject="FaceSec Sync Error",
                                            body=error_message,
                                            sender_email=SENDER_EMAIL,
                                            sender_name=SENDER_NAME,
                                            to_email=EMAIL_USER
                                        )
                            else:
                                error_message = "Image path not found in uploaded image data."
                                print(error_message)
                                send_sms(YOUR_PHONE_NUMBER, error_message)
                                send_email(
                                    subject="FaceSec Sync Error",
                                    body=error_message,
                                    sender_email=SENDER_EMAIL,
                                    sender_name=SENDER_NAME,
                                    to_email=EMAIL_USER
                                )
                                logout_to_facesec(cookies)
                                print("Logged out from FaceSec API")
                        else:
                            error_message = "Failed to upload image."
                            print(error_message)
                            send_sms(YOUR_PHONE_NUMBER, error_message)
                            send_email(
                                subject="FaceSec Sync Error",
                                body=error_message,
                                sender_email=SENDER_EMAIL,
                                sender_name=SENDER_NAME,
                                to_email=EMAIL_USER
                            )
                            logout_to_facesec(cookies)
                            print("Logged out from FaceSec API")
                    else:
                        error_message = "Failed to retrieve rule ID."
                        print(error_message)
                        send_sms(YOUR_PHONE_NUMBER, error_message)
                        send_email(
                            subject="FaceSec Sync Error",
                            body=error_message,
                            sender_email=SENDER_EMAIL,
                            sender_name=SENDER_NAME,
                            to_email=EMAIL_USER
                        )
                else:
                    error_message = "Failed to retrieve user information from HYDRA."
                    print(error_message)
                    send_sms(YOUR_PHONE_NUMBER, error_message)
                    send_email(
                        subject="FaceSec Sync Error",
                        body=error_message,
                        sender_email=SENDER_EMAIL,
                        sender_name=SENDER_NAME,
                        to_email=EMAIL_USER
                    )
                    logout_to_facesec(cookies)
                    print("Logged out from FaceSec API")
            else:
                error_message = "Failed to retrieve personnel list from FaceSec."
                print(error_message)
                send_sms(YOUR_PHONE_NUMBER, error_message)
                send_email(
                    subject="FaceSec Sync Error",
                    body=error_message,
                    sender_email=SENDER_EMAIL,
                    sender_name=SENDER_NAME,
                    to_email=EMAIL_USER
                )
                logout_to_facesec(cookies)
                print("Logged out from FaceSec API")
        except ValueError as e:
            error_message = str(e)
            print(error_message)
            send_sms(YOUR_PHONE_NUMBER, error_message)
            send_email(
                subject="FaceSec Sync Error",
                body=error_message,
                sender_email=SENDER_EMAIL,
                sender_name=SENDER_NAME,
                to_email=EMAIL_USER
            )
            logout_to_facesec(cookies)
            print("Logged out from FaceSec API")
        except (TypeError, AttributeError) as e:
            error_message = f"Error occurred: {e}. Check if the data retrieved is as expected."
            print(error_message)
            send_sms(YOUR_PHONE_NUMBER, error_message)
            send_email(
                subject="FaceSec Sync Error",
                body=error_message,
                sender_email=SENDER_EMAIL,
                sender_name=SENDER_NAME,
                to_email=EMAIL_USER
            )
            logout_to_facesec(cookies)
            print("Logged out from FaceSec API")
    else:
        error_message = "Failed to login to FaceSec API."
        print(error_message)
        send_sms(YOUR_PHONE_NUMBER, error_message)
        send_email(
            subject="FaceSec Sync Error",
            body=error_message,
            sender_email=SENDER_EMAIL,
            sender_name=SENDER_NAME,
            to_email=EMAIL_USER
        )
