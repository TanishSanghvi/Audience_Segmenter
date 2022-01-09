
import os
os.chdir('/Users/apple/Desktop/IUB/Data Mining/Final Project/Datasets')
import pandas as pd
from datetime import datetime
import googleapiclient.discovery
import googleapiclient.errors
import datetime


def auth(i):
    scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
    
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    
    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = ['AIzaSyAuo70sj6mxFGfpfKK-kj5vA4YPBwa7cZM', 'AIzaSyBz0rStW1NDfHjzyBKOCFud7RS0sfqEs04', 
                     'AIzaSyBo1YHUZrL1Rt_KYvR6s1sTDqnX394Zd50', 'AIzaSyDIs7gvKx6NnqWUjXB8JfAf3hrCsAZti3o']
    
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY[i])
    
    return youtube

playlist_file = pd.read_excel('travel_playlists.xlsx')
playlist_list = list(set(playlist_file['playlist_id']))

videos = []
error=[]
count=0

auth_val = 0
youtube = auth(auth_val)

#get max 50 videos from each playlist
for playlist in playlist_list:
    count+=1
    print(count, playlist)
    
    try:
        request = youtube.playlistItems().list(
            part="snippet",
            maxResults=50,
            playlistId=playlist
            )
        response = request.execute()
        print (response['pageInfo']['totalResults'])
        videos.extend(response['items'])
        # try:
        #     request = youtube.playlistItems().list(
        #         part="snippet",
        #         maxResults=50,
        #         pageToken = response['nextPageToken'],
        #         playlistId=playlist
        #     )
        #     response = request.execute()
        #     videos.extend(response['items'])
        #     print('100 done..')
        # except:
        #     pass
    except:
        error.append(playlist)
        print('Rate Limit Exceeded Maybe..')
        break;

df = pd.DataFrame(columns=['video_in_playlist','playlist_channel_id','playlist_channelTitle','video_id','videoTitle','added_to_playlist'])

count=0
for v in videos:
    count+=1
    if count%5==0:
        print(count)
    values = []
    values.append(v['snippet']['playlistId'])
    values.append(v['snippet']['channelId'])
    values.append(v['snippet']['channelTitle'])
    values.append(v['snippet']['resourceId']['videoId'])
    values.append(v['snippet']['title'])
    date = datetime.datetime.strptime(v['snippet']['publishedAt'],'%Y-%m-%dT%H:%M:%SZ')
    values.append(datetime.datetime.strftime(date,'%Y-%m-%d'))
    df = df.append(pd.Series(values, index=['video_in_playlist','playlist_channel_id','playlist_channelTitle','video_id','videoTitle','added_to_playlist']),ignore_index=True)
 
df.to_excel('travel_all_videos.xlsx', index=False)

