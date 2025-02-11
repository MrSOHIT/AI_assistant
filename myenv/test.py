import requests

newsapi = "your_api_key"
response = requests.get(f"https://newsapi.org/v2/top-headlines?country=us&apiKey={newsapi}")

print("Status Code:", response.status_code)
print("Response Content:", response.json())
