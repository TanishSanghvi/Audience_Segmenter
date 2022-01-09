
import pytz
import os
import pandas as pd
from datetime import datetime
import googleapiclient.discovery
import googleapiclient.errors
import datetime

est = pytz.timezone('US/Eastern')

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

# video_list = []

videos = pd.read_excel('travel_all_videos.xlsx')
video_list = list(set(videos['video_id']))

df = pd.DataFrame(columns=['video_id','title','publishedAt_Time','tags','categories','video_channel_title','video_channel_id'])

auth_val = 0
youtube = auth(auth_val)

#pulling tags for 25 videos with each call
for i in range(0, len(video_list), 25):

    batch_ids=video_list[i:i+25]
    print(i+25)
    
    request = youtube.videos().list(
        part="snippet",
        id=batch_ids
    )
    
    response = request.execute()
    if response['items']:
        for resp in response['items']:
            v=resp['snippet']
            try:
                dt_est = est.fromutc(datetime.datetime.strptime(v['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')).strftime('%Y-%m-%d %H:%M:%S')
                dt = datetime.datetime.strptime(v['publishedAt'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S')       
            except:
                dt_est = est.fromutc(datetime.datetime.strptime(v['publishedAt'], '%Y-%m-%dT%H:%M:%S.000Z')).strftime('%Y-%m-%d %H:%M:%S')
                dt = datetime.datetime.strptime(v['publishedAt'], '%Y-%m-%dT%H:%M:%S.000Z').strftime('%Y-%m-%d %H:%M:%S')
            try:
                tags = v['tags']
            except:
                tags=[]
            val = [resp['id'],v['localized']['title'],dt,tags,v['categoryId'],v['channelTitle'],v['channelId']]
            df.loc[len(df)] = val
    else:
        print('Rate Limit Exceeded maybe..')
        break;


df.to_excel('travel_video_tags_ytapi.xlsx', index=False)
