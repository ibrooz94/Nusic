import requests
import json 
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
from auth import getToken

def getSpotify():
    # Spotify Api call for meta data

    token = getToken() 

    f = open('YT_results.json')
    yt_result = json.load(f)

    track = yt_result['title']
    artist = yt_result['artist']

    # get genre meta data info from spotify -- CAN BE IMPOROVED
    url = f"https://api.spotify.com/v1/search?q={track}%20{artist}&type=track,artist&limit=1"
    headers = {
    'Content-Type': 'application/json',
    'Authorization' : f'Bearer {token}'
    }
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json()

        # with open('spotify_debug_data.json', 'w', encoding='utf-8') as f:
        #     json.dump(data, f, ensure_ascii=False, indent=4)

    else:
        print("there's been an error")

    spotify_results = {}
    if data.get('error'):
        print("Access token has expired!")
        spotify_results['spotify'] = "False"
        return False
    else:
        try:
            spotify_results['spotify'] = "True"
            spotify_results['title'] = data['tracks']['items'][0]['name']
            spotify_results['album']=data['tracks']['items'][0]['album']['name']
            spotify_results['year']=str(data['tracks']['items'][0]['album']['release_date'])[0:4]
            spotify_results['image'] = data['tracks']['items'][0]['album']['images'][0]['url']
            spotify_results['track_number'] = data['tracks']['items'][0]['track_number']
            spotify_results['total_tracks'] = data['tracks']['items'][0]['album']['total_tracks']
            spotify_results['artist_id'] = data['tracks']['items'][0]['album']['artists'][0]['id']

            # get genre data using artist endpoint
            url = r"https://api.spotify.com/v1/artists/{}".format(spotify_results['artist_id'])
            headers = {
            'Content-Type': 'application/json',
            'Authorization' : 'Bearer {}'.format(token)
            }
            r = requests.get(url, headers=headers)
            genre_data = r.json()

            # with open('genre_debug_data.json', 'w', encoding='utf-8') as f:
            #         json.dump(genre_data, f, ensure_ascii=False, indent=4)

            try:
                spotify_results['genre'] = genre_data['genres'][0]  # gets the first genre
            except IndexError:
                spotify_results['genre'] = ""

            try:
                spotify_results['artist'] = data['artists']['items'][0]['name']
            except IndexError:
                spotify_results['artist'] = data['tracks']['items'][0]['album']['artists'][0]['name']
            
            with open('spotify_results.json', 'w', encoding='utf-8') as f:
                json.dump(spotify_results, f, ensure_ascii=False, indent=4)

        except Exception as e:
            print("getSpotify: "+ str(e))
            print("Skip... ")
            return False

    return True

def spotifyTags(file=None):
    
    # Open results json file from getSP
    f = open('spotify_results.json')
    spotify_tag = json.load(f)

    # download cover image
    img_url = spotify_tag['image']
    r = requests.get(img_url, stream=True)
    if r.status_code == 200:
        with open('cover.jpg', 'wb') as f:
            for chunk in r:
                f.write(chunk)

    audio_path = file
    picture_path = 'cover.jpg'

    # Text based tags
    audio = EasyID3(audio_path)
    audio['title'] = spotify_tag['title']
    audio['album'] = spotify_tag['album']
    audio['artist'] = spotify_tag['artist']
    audio['date'] = spotify_tag['year']
    audio['tracknumber'] = str(spotify_tag['track_number'])
    audio['genre'] = spotify_tag['genre']
    audio.save()  # save the current changes

    # Add image
    image_tag = MP3(audio_path, ID3=ID3)
    image_tag.tags.add(APIC(mime='image/jpeg',type=3,desc=u'Cover',data=open(picture_path,'rb').read()))
    image_tag.save()

    print('[SPOTIFY-TAGS: DONE]')

if __name__ == "__main__":
    getSpotify()
