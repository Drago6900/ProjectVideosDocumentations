import requests
import json

# FaceSec API endpoints
FACESEC_LOGIN_URL = "http://172.17.170.105:8081/api/account/login?password=2580"
FACESEC_PERSONS_URL = "http://172.17.170.105:8081/api/persons?size=100&page=0"

# HYDRA API endpoint
HYDRA_URL = "https://mip-10741p.mpdv.cloud:8080/data/BOPerson/list?X-Access-Id=00010741"

def login_to_facesec():
    try:
        response = requests.get(FACESEC_LOGIN_URL)
        if response.status_code == 200:
            print("Successfully logged in to FaceSec API")
            return response.cookies
    except requests.RequestException as e:
        print(f"Error logging into FaceSec API: {e}")
    print("Failed to login to FaceSec API")
    return None

def access_personnel_list(cookies):
    try:
        response = requests.get(FACESEC_PERSONS_URL, cookies=cookies)
        if response.status_code == 200:
            print("Successfully accessed personnel list from FaceSec API")
            return response.json()
    except requests.RequestException as e:
        print(f"Error accessing personnel list from FaceSec API: {e}")
    print("Failed to access personnel list from FaceSec API")
    return None

def get_user_info_from_hydra():
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

def compare_data(facesec_data, hydra_data):
    # Extracting 'name' and 'no' from FaceSec data
    facesec_dict = {(entry['name'], entry['no']) for entry in facesec_data['entity']['content']}

    # Extracting 'person.name' and 'person.card_id' from HYDRA data
    hydra_dict = {(entry['data'][1], entry['data'][0]) for entry in hydra_data[1:]}

    # Finding common entries
    matching_users = facesec_dict.intersection(hydra_dict)
    
    # Finding HYDRA entries not in FaceSec
    non_matching_hydra = hydra_dict - facesec_dict

    # Prepare the result
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

if __name__ == '__main__':
    cookies = login_to_facesec()
    if cookies:
        facesec_data = access_personnel_list(cookies)
        if facesec_data:
            hydra_data = get_user_info_from_hydra()
            if hydra_data:
                comparison_result = compare_data(facesec_data, hydra_data)
                
                # Pretty print the comparison result
                pretty_printed_result = json.dumps(comparison_result, indent=4)
                print(pretty_printed_result)
            else:
                print("Failed to retrieve user information from HYDRA")
        else:
            print("Failed to retrieve user information from FaceSec")
    else:
        print("Failed to login to FaceSec API")
