import json
import requests

# FaceSec API endpoints PLEASE CHANGE IP ADDRESSES to FaceSec IP
FACESEC_LOGIN_URL = "http://172.17.171.58:8081/api/account/login?password=25802580"
FACESEC_PERSONS_URL = "http://172.17.171.58:8081/api/persons?size=100&page=0"
FACESEC_RULES_URL = "http://172.17.171.58:8081/api/rules"
FACESEC_ADD_PERSONNEL_URL = "http://172.17.171.58:8081/api/person"
FACESEC_UPLOAD_IMAGE_URL = "http://172.17.171.58:8081/api/upload/image"

# HYDRA API endpoint
HYDRA_URL = "https://mip-10741p.mpdv.cloud:8080/data/BOPerson/list?X-Access-Id=00010741"

# Global variables to store uploaded image data and rule ID
uploaded_image_data = None
rule_id = None

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

async def compare():
    cookies = await login_to_facesec()
    if cookies:
        facesec_data = await access_personnel_list(cookies)
        if facesec_data:
            hydra_data = await get_user_info_from_hydra()
            if hydra_data:
                comparison_result = await compare_data(facesec_data, hydra_data)
                
                pretty_printed_result = json.dumps(comparison_result, indent=4)
                print(pretty_printed_result)

                if await retrieve_identification_rules(cookies):
                    print("Retrieved rule ID:", rule_id)

                    image_file_path = "C:/Users/Hadrian Yeo/Documents/Images/face.jpg" ##Change this file path to the image of the guy's face in the personnel's list

                    uploaded_image_data = await upload_image(image_file_path, FACESEC_UPLOAD_IMAGE_URL, cookies)
                    if uploaded_image_data:
                        print("Uploaded image data:", uploaded_image_data)

                        image_path = uploaded_image_data.get("entity", "")
                        if image_path:
                            print("Image path:", image_path)

                            # Sort non-matching personnel by their number
                            sorted_non_matching_hydra = sorted(comparison_result["non_matching_hydra"], key=lambda x: x["no"])

                            for person in sorted_non_matching_hydra:
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

                                if await add_personnel_to_facesec(personnel_data, cookies):
                                    print(f"Personnel {person['name']} added successfully!")
                                else:
                                    print(f"Failed to add personnel {person['name']}.")
                        else:
                            print("Image path not found in uploaded image data.")
                    else:
                        print("Failed to upload image.")
            else:
                print("Failed to retrieve user information from HYDRA")
        else:
            print("Failed to retrieve user information from FaceSec")
    else:
        print("Failed to login to FaceSec API")
