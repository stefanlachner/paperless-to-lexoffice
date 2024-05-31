import requests
from time import sleep

def upload_voucher(access_token, url, filepath):

    

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }

    files = {
        "file": open(filepath, "rb"),
        "type": (None, "voucher"),
    }

    sleep(0.5)
    response = requests.post(url, headers=headers, files=files)

    # Print the response from the server
    if response.status_code == 202:
        print(f"Document has lexoffice UUID {response.json().get('id')}")
    else:
        print(f"Error uploading: {response.status_code}")
    
    

    return response
