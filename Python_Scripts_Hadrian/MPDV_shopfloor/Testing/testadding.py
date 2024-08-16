import requests
import json

# FaceSec API endpoints
FACESEC_LOGIN_URL = "http://172.17.170.105:8081/api/account/login?password=2580"
FACESEC_PERSONS_URL = "http://172.17.170.105:8081/api/persons?size=100&page=0"
FACESEC_RULES_URL = "http://172.17.170.105:8081/api/rules"
FACESEC_ADD_PERSONNEL_URL = "http://172.17.170.105:8081/api/person"
FACESEC_UPLOAD_IMAGE_URL = "http://172.17.170.105:8081/api/upload/image"

# Global variables to store uploaded image data and rule ID
uploaded_image_data = None
rule_id = None

def login_to_facesec():
    try:
        response = requests.get(FACESEC_LOGIN_URL)
        if response.status_code == 200:
            print("Successfully logged in to FaceSec API")
            # Return cookies for further use
            return response.cookies
        else:
            print(f"Failed to login. Status code: {response.status_code}, Response: {response.text}")
    except requests.RequestException as e:
        print(f"Error logging into FaceSec API: {e}")

    print("Failed to login to FaceSec API")
    return None

def access_personnel_list(cookies):
    try:
        response = requests.get(FACESEC_PERSONS_URL, cookies=cookies)
        if response.status_code == 200:
            print("Successfully accessed personnel list:")
            personnel_data = response.json()
            # Pretty print the JSON response
            pretty_printed_data = json.dumps(personnel_data, indent=4)
            print(pretty_printed_data)
            return personnel_data
        else:
            print(f"Failed to access personnel list. Status code: {response.status_code}, Response: {response.text}")
    except requests.RequestException as e:
        print(f"Error accessing personnel list: {e}")

    print("Failed to access personnel list")
    return None

def retrieve_identification_rules(cookies):
    global rule_id  # Use the global variable for rule_id

    try:
        response = requests.get(FACESEC_RULES_URL, cookies=cookies)
        if response.status_code == 200:
            print("Successfully accessed identification rules:")
            rules_data = response.json()
            print("Raw rules data:", rules_data)  # Debugging line to see the structure of rules_data

            # Access the list of rules from the 'entity' key
            if isinstance(rules_data, dict) and 'entity' in rules_data:
                rules = rules_data['entity']
            else:
                print("Unexpected data structure for rules:", type(rules_data))
                return False

            if isinstance(rules, list) and rules:
                # Extract and print rule id and name
                rules_info = [{'id': rule['id'], 'name': rule['name']} for rule in rules]
                pretty_printed_rules = json.dumps(rules_info, indent=4)
                print(pretty_printed_rules)

                rule_id = rules_info[0]['id']  # Use the first rule ID for the example
                return True
            else:
                print("Unexpected data structure for rules:", type(rules))
        else:
            print(f"Failed to access rules. Status code: {response.status_code}, Response: {response.text}")
    except requests.RequestException as e:
        print(f"Error accessing identification rules: {e}")

    print("Failed to access identification rules")
    return False

def upload_image(image_file_path, upload_url, cookies):
    global uploaded_image_data  # Using the global variable
    
    if uploaded_image_data:
        print("Image already uploaded. Reusing existing imagePath:", uploaded_image_data.get("imagePath", ""))
        return uploaded_image_data
    
    try:
        with open(image_file_path, 'rb') as file:
            files = {'file': (image_file_path, file, 'image/jpeg')}  # Specify file field name and content type
            response = requests.post(upload_url, files=files, cookies=cookies)
            if response.status_code == 200:
                uploaded_image_data = response.json()  # Storing uploaded image data
                print("Image uploaded successfully")
                return uploaded_image_data
            else:
                print(f"Failed to upload image. Status code: {response.status_code}, Response: {response.text}")
    except FileNotFoundError:
        print(f"File not found: {image_file_path}")
    except requests.RequestException as e:
        print(f"Error uploading image: {e}")
    return None

def add_personnel_to_facesec(personnel_data, cookies):
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
            print("Response:", response.json())  # Print the response for debugging
    except requests.RequestException as e:
        print(f"Error adding personnel to FaceSec: {e}")
    return False

if __name__ == '__main__':
    # Login to FaceSec API to obtain cookies
    cookies = login_to_facesec()
    if cookies:
        # Access personnel list using obtained cookies
        personnel_data = access_personnel_list(cookies)
        if personnel_data:
            # Retrieve identification rules using obtained cookies
            if retrieve_identification_rules(cookies):
                print("Retrieved rule ID:", rule_id)

                # Example image file path
                image_file_path = "C:/Users/limmi/Downloads/face.jpg"
                
                # Upload image
                uploaded_image_data = upload_image(image_file_path, FACESEC_UPLOAD_IMAGE_URL, cookies)
                if uploaded_image_data:
                    print("Uploaded image data:", uploaded_image_data)

                    # Extract image path from uploaded image data
                    image_path = uploaded_image_data.get("entity", "")
                    if image_path:
                        print("Image path:", image_path)

                        # Construct personnel data with image path
                        personnel_data = {
                            "name": "Person 13",
                            "no": "5513",
                            "idCard": "",
                            "ruleId": rule_id,  # Using the retrieved rule ID
                            "icNumber": "",
                            "wgNumber": "",
                            "groupId": "",  # Using the organization name
                            "imagePath": image_path  # Using the 'entity' value as the image path
                        }

                        # Print personnel data for debugging
                        print("Personnel data being sent:", json.dumps(personnel_data, indent=4))

                        # Add personnel to FaceSec
                        if add_personnel_to_facesec(personnel_data, cookies):
                            print("Personnel added successfully!")
                        else:
                            print("Failed to add personnel.")
                    else:
                        print("Image path not found in uploaded image data.")
                else:
                    print("Failed to upload image.")
