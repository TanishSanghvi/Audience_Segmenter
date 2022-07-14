#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 22:46:05 2022

@author: apple
"""

import pandas as pd
import pytz
import datetime

class Tags:
    
    def __init__(self, youtube):
        self.youtube = youtube
        
    def pull_tags(self, videos):
        
        est = pytz.timezone('US/Eastern')
        video_list = list(set(videos['video_id']))
        
        tags_df = pd.DataFrame(columns=['video_id','title','publishedAt_Time','tags','categories','video_channel_title','video_channel_id'])
        
        print('Extracting tags..')
        
        for i in range(0, len(video_list), 25):
    
            batch_ids=video_list[i:i+25]
            print(i+25)
            
            request = self.youtube.videos().list(
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
                    tags_df.loc[len(tags_df)] = val
            else:
                print('Rate Limit Exceeded maybe..')
                break;
        
        print('Tags extracted..')
        return tags_df


    def process(self, videos, playlists, tags):
        #tags = pd.read_csv('/Users/apple/Downloads/flask/tags.csv')
        print('Processing data..')
        
        df = tags[['video_id','tags']]
        df['tags'] = df['tags'].map(lambda x: str(x))
        df['tags'] = df['tags'].map(lambda x: x.strip("[]")) #remove the [] from the tags
        df = df.assign(tags=df.tags.str.split(",")).explode('tags') #put each tag on a diff line
        df = df[df['tags'].astype(bool)].reset_index(drop = True)
        df['tags'] = df['tags'].map(lambda x: eval(x)) # remove quotes
        df['tags'] = df['tags'].map(lambda x: x.strip()) # rempve whitespaces
        df_video_unique_tags = df.drop_duplicates()
        
        df_commenter_playlist = playlists
        df_commenter_playlist.rename(columns={'commenter_channelTitle':'commenter'},inplace=True)
        df_commenter_playlist = df_commenter_playlist[['commenter','commenter_channel_id','playlist_id']]
        
        df_playlist_video = videos
        df_playlist_video.rename(columns={'video_in_playlist':'playlist_id'},inplace=True)
        df_playlist_video = df_playlist_video[['playlist_id','video_id','videoTitle','added_to_playlist','playlist_channel_id','playlist_channelTitle']]
                
        df_commenter_with_videos_in_playlist = pd.merge(df_commenter_playlist, df_playlist_video, on='playlist_id', how='outer')
        df_commenter_with_videos_in_playlist.drop(columns=['playlist_channel_id','playlist_channelTitle'],inplace=True)
        
        df_commenter_with_tags_for_videos = pd.merge(df_commenter_with_videos_in_playlist, df_video_unique_tags, on='video_id', how='left')
        commenters_with_tags = df_commenter_with_tags_for_videos.dropna(subset=['tags'])
        commenters_with_tags.reset_index(inplace=True)
        
        return commenters_with_tags
        