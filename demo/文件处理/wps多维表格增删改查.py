import requests

api_url = "https://api.wps.com/v1/documents"

headers = {

    "Authorization": "Bearer YOUR_ACCESS_TOKEN",

    "Content-Type": "application/json"

}

params = {

    "document_id": "123456",

    "action": "read"

}

response = requests.get(api_url, headers=headers, params=params)

if response.status_code == 200:

    document_data = response.json()

    print("Document data:", document_data)


else:

    print("API request failed with status code:", response.status_code)
