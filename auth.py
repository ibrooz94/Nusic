import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()

def getToken():
    client_id = os.environ.get("client_id")
    client_secret = os.environ.get("client_secret")


    client_creds = f"{client_id}:{client_secret}"
    client_creds_b = base64.b64encode(client_creds.encode('ascii'))

    token_url = 'https://accounts.spotify.com/api/token'
    token_data = {
        'grant_type': 'client_credentials'
    }
    token_headers = {
        "Authorization": f'Basic {client_creds_b.decode()}'
    }

    r = requests.post(token_url,data = token_data, headers = token_headers )
    data = r.json()
    return data['access_token']
    
if __name__ == "__main__":
    getToken()