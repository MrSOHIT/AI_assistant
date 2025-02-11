import requests

newsapi = "2e14f25cf0ea4eb6bb425c8ebc4eab22"
response = requests.get(f"https://newsapi.org/v2/top-headlines?country=us&apiKey={newsapi}")

print("Status Code:", response.status_code)
print("Response Content:", response.json())