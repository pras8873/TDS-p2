import requests

url = "http://localhost:8000/quiz"
payload = {
    "email": "21f2000973@ds.study.iitm.ac.in",
    "secret": "nishant",  # must match your .env
    "url": "https://tds-llm-analysis.s-anand.net/demo"
}

response = requests.post(url, json=payload)
print("Status code:", response.status_code)
print("Response:", response.json())
