# import packages
import requests
import json
import youtube_dl
import sys
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error, TIT2, TALB, TPE1
from ytmusicapi import YTMusic
from getSpotify import getSpotify, spotifyTags

class Music:
    def __init__(self):
        pass

    def get_search_result(self, i, j):
        # Search for song

        print("[FETCH INITIALIZED]")
        try:
            ytmusic = YTMusic()
            data= ytmusic.search(query = i + " " + j, filter="songs")
        except requests.exceptions.ConnectionError:
            print("get_search_result: Connection Error")
            sys.exit(1)     
        except Exception:
            raise
        
        search_result = []
        for i in data:
            search_result.append({
                'artist': i.get('artists', None)[0]['name'],
                'title': i['title'],
                'videoId':i['videoId'],
                'image': i['thumbnails'][1]['url'],
                'album': i['album']['name']
                })
        
        print("\nSearch results") # display search results
        for i, j in enumerate(search_result):
            a = j['artist']
            print(i + 1, " - " + j["title"] + " - " + str(a))

        choice = int(input("\nEnter the number of your choice::: ")) # User Selection feature
        selection = search_result[choice - 1]

        try:
            album_art_url = ytmusic.get_song(selection['videoId'])
            album_art = album_art_url['videoDetails']['thumbnail']['thumbnails'][3]['url']
            selection['image'] = album_art
        except Exception:
            pass
        
        # write user selection search result to json file 
        with open('YT_results.json', 'w', encoding='utf-8') as f:
            json.dump(selection, f, ensure_ascii=False, indent=4)

        self.selection = selection

        return selection

    def download_selection(self, i, j, video_id=None):

        # f = open('YT_results.json')          #
        # yt_result = json.load(f)             #--deprecated
        # video_id = yt_result['videoId']      #

        video_id = self.get_search_result(i , j)['videoId']

        if video_id:
            link = 'http://www.youtube.com/watch?v={}'.format(video_id)
        else: 
            print("download: No videoId found")
            sys.exit(1)

        # download and conversion using ffmpeg
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors':[{
                'key':'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'ffmpeg-location': './',
            'outmpl': "./%(id)s.%(ext)s"
        }
        _id = link.strip()

        try:
            meta = youtube_dl.YoutubeDL(ydl_opts).extract_info(_id)
            save_location = meta['title']+ "-" + meta['id'] + ".mp3"

        except youtube_dl.utils.DownloadError:
            print("down_it CONNECTION ERROR")
            sys.exit()

        return save_location

    def ytTags(self, file=None):

        f = open('YT_results.json')
        results = json.load(f)

        # download cover image
        img_url = results['image'] 
        r = requests.get(img_url, stream=True)
        if r.status_code == 200:
            with open('cover.jpg', 'wb') as f:
                for chunk in r:
                    f.write(chunk)

        audio_path = file
        picture_path = 'cover.jpg'

        audio = MP3(audio_path, ID3=ID3)

        try:
            audio.add_tags()
        except error:
            pass

        audio.tags.add(APIC(mime='image/jpeg',type=3,desc=u'Cover',data=open(picture_path,'rb').read()))

        audio["TIT2"] = TIT2(encoding=3, text= results['title']) #song name,(title)
        audio["TALB"] = TALB(encoding=3, text= results['album']) #album
        audio["TPE1"] = TPE1(encoding=3, text= results['artist']) # artist

        audio.save()  # save the current changes

        print('[YT-TAGS: DONE]')

    def addTags(self, i, j):

        file = self.download_selection(i, j)
        try:
            # spotify_status = False # Turn off spotify fetch
            spotify_status = getSpotify()
            if spotify_status:
                spotifyTags(file)
            else:
                self.ytTags(file)

        except requests.exceptions.ConnectionError:
            print('CONNECTION ERROR')
            sys.exit()

music = Music()

if __name__ == "__main__":
    i = str(input("Name? >> "))
    j = str(input("Track? >> "))

    music.addTags(i , j)

    # Program Flow:
    #     addTags |calls download_selection
    #                         |calls get_search_result