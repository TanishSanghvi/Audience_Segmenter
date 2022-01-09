

#pip install --upgrade google-api-python-client
#pip install google-api-core
import os
os.chdir('/Users/apple/Desktop/IUB/Data Mining/Final Project/Datasets')
import pandas as pd
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = 'AIzaSyAyUcZDRaAYpFY6Ck73nlZjQZGkkSuiSSg'

youtube = googleapiclient.discovery.build(
    api_service_name, api_version, developerKey = DEVELOPER_KEY)

comment_file = pd.read_excel('travel_comments.xlsx')
channel_list = list(set(comment_file['commenter_channel_id']))

error=[]
playlist = []
count=0

for channelId in channel_list:
    count+=1
    print(count, channelId)
    try:
        request = youtube.playlists().list(
            part="snippet",
            channelId=channelId
        )
        response = request.execute()
        print ('Playlists = ', response['pageInfo']['totalResults'])
        playlist.extend(response['items'])
        # if the nextPageToken is returned, get more comments. 
        #There is a limit for the # of comments you can get in a day
        try:
            items=5
            while response['nextPageToken']:
                if items>20:                   # Sampling for max 20 playlists per user
                    print('20 exceeded')
                    break;
                else:
                    request = youtube.playlists().list(
                        part="snippet",
                        pageToken = response['nextPageToken'],
                        channelId=channelId
                        )
                    response = request.execute()
                    playlist.extend(response['items'])
                    items+=5
        except:
            pass
    except:
        print('Rate Limit exceeded..')
        error.append(channelId)

        
df = pd.DataFrame(columns=['playlist_id','commenter_channel_id','commenter_channelTitle'])

count = 0
for p in playlist:
    count+=1
    print(count)
    values = []
    try:
        values.append(p['id'])
        values.append(p['snippet']['channelId'])
        values.append(p['snippet']['channelTitle'])
        df = df.append(pd.Series(values, index=['playlist_id','commenter_channel_id','commenter_channelTitle']),ignore_index=True)
    except:
        pass

df.to_excel('travel_playlists.xlsx', index=False)





