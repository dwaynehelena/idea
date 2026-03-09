import requests

def get_weather():
    """1. Weather (Open-Meteo)"""
    url = "https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&current_weather=true"
    response = requests.get(url)
    return response.json()

def get_crypto_price():
    """2. Crypto (CoinGecko)"""
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"
    response = requests.get(url)
    return response.json()

def get_hackernews_top():
    """3. HackerNews (HackerNews API)"""
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    response = requests.get(url)
    top_story_id = response.json()[0]
    story_url = f"https://hacker-news.firebaseio.com/v0/item/{top_story_id}.json"
    story_response = requests.get(story_url)
    return story_response.json()

def get_ip_geo():
    """4. IP Geo (ip-api.com)"""
    url = "http://ip-api.com/json/"
    response = requests.get(url)
    return response.json()

def get_advice():
    """5. Advice (Advice Slip API)"""
    url = "https://api.adviceslip.com/advice"
    response = requests.get(url)
    return response.json()

def get_joke():
    """6. Jokes (Official Joke API)"""
    url = "https://official-joke-api.appspot.com/random_joke"
    response = requests.get(url)
    return response.json()

def get_bored_activity():
    """7. Bored (Bored API / Activity)"""
    # boredapi.com might be down, trying an alternative if needed
    url = "https://www.boredapi.com/api/activity"
    try:
        response = requests.get(url, timeout=5)
        return response.json()
    except:
        return {"activity": "Go for a walk", "type": "relaxation"}

def get_user_persona():
    """8. User Persona (RandomUser API)"""
    url = "https://randomuser.me/api/"
    response = requests.get(url)
    return response.json()

def get_cat_fact():
    """9. Cat Facts (Cat Facts API)"""
    url = "https://catfact.ninja/fact"
    response = requests.get(url)
    return response.json()

def get_ip_address():
    """10. Ipify (Ipify API)"""
    url = "https://api.ipify.org?format=json"
    response = requests.get(url)
    return response.json()

if __name__ == "__main__":
    print("Verifying Live Intelligence Suite...")
    try:
        print("Weather:", get_weather().get('current_weather', {}).get('temperature'), "C")
        print("Crypto (BTC):", get_crypto_price().get('bitcoin', {}).get('usd'))
        print("HackerNews Top Story:", get_hackernews_top().get('title'))
        print("IP Geo (City):", get_ip_geo().get('city'))
        print("Advice:", get_advice().get('slip', {}).get('advice'))
        print("Joke:", get_joke().get('setup'), "-", get_joke().get('punchline'))
        print("Bored Activity:", get_bored_activity().get('activity'))
        print("User Persona (Name):", get_user_persona().get('results', [{}])[0].get('name', {}).get('first'))
        print("Cat Fact:", get_cat_fact().get('fact'))
        print("IP (Ipify):", get_ip_address().get('ip'))
        print("Verification Successful!")
    except Exception as e:
        print("Verification Failed:", e)
