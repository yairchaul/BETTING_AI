import requests

print("🔍 PROBANDO CON THE ODDS API")
print("=" * 60)

API_KEY = "98ccdb7d4c28042caa8bc8fe7ff6cc62"
url = "https://api.the-odds-api.com/v4/sports"

params = {
    "apiKey": API_KEY
}

try:
    response = requests.get(url, params=params)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        sports = response.json()
        print(f"✅ Deportes disponibles: {len(sports)}")
        for sport in sports[:5]:
            print(f"  - {sport['title']} ({sport['key']})")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text[:200])
except Exception as e:
    print(f"Error: {e}")

print("=" * 60)
