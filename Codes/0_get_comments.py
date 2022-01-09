
import os
os.chdir('/Users/apple/Desktop/IUB/Data Mining/Final Project/Datasets')
import pandas as pd
import googleapiclient.discovery
import datetime
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import math

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# https://console.cloud.google.com/apis/credentials?folder=&organizationId=&project=aerobic-inkwell-266413
api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = 'AIzaSyAyUcZDRaAYpFY6Ck73nlZjQZGkkSuiSSg'

youtube = googleapiclient.discovery.build(
    api_service_name, api_version, developerKey = DEVELOPER_KEY)


# pass the list of videos for which you need the comments
df=pd.read_csv('/Users/apple/Downloads/YouTube Titles and description using youtube api.csv')
df = df[df['Category']=='travel']
#df['Video_id']=df['Video_URL'].apply(lambda x: x.split('=')[1])

video_list=df['Video Id']

comments = []
error=[]
df = pd.DataFrame(columns=['video_id','comment_id','commenter_Name','commenter_channel_id'])

#get the 1st 100 comments
count=0
for videoId in video_list:
    count+=1
    print(count, videoId)
    try:
        request = youtube.commentThreads().list(
            part="snippet,replies",
            maxResults=100,
            videoId=videoId
        )
        response = request.execute()
        comments.extend(response['items'])
        # if the nextPageToken is returned, get more comments. 
        #There is a limit for the # of comments you can get in a day
        # try:
        #     while response['nextPageToken']:
        #         request = youtube.commentThreads().list(
        #             part="snippet,replies",
        #             maxResults=100,
        #             pageToken = response['nextPageToken'],
        #             videoId=videoId,
        #         )
        #         response = request.execute()
        #         comments.extend(response['items'])
        # except:
        #     pass
    except:
        error.append(videoId)
        continue

count = 0
#to get the replies for the comments
for c in comments:
    count+=1
    print(count)
    try:
        if c['replies']:
            for r in c['replies']['comments']:
                values = []
                values.append(r['snippet']['videoId'])
                values.append(r['id'])
                values.append(r['snippet']['authorDisplayName'])
                try:
                    values.append(r['snippet']['authorChannelId']['value'])
                except:
                    values.append('')
                df = df.append(pd.Series(values, index=['video_id','comment_id','commenter_Name','commenter_channel_id']),ignore_index=True)
    except:
        values = []
        values.append(r['snippet']['videoId'])
        values.append(r['id'])
        values.append(r['snippet']['authorDisplayName'])
        try:
            values.append(r['snippet']['authorChannelId']['value'])
        except:
            values.append('')
        df = df.append(pd.Series(values, index=['video_id','comment_id','commenter_Name','commenter_channel_id']),ignore_index=True)

    
df.to_excel('travel_comments.xlsx', index=False)

    
    
    
    
    
    