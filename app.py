import requests

API_KEY = "TA_CLE_API"

url = "https://api.pdf.ai/v1/extract"

headers = {
    "Authorization": f"Bearer {API_KEY}"
}

files = {
    "file": open("audit.pdf", "rb")
}

data = {
    "prompt": "Extrais les KPI du document : nombre de OK, NOK, sections, score qualité"
}

response = requests.post(url, headers=headers, files=files, data=data)

print(response.json())
