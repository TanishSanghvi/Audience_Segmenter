import pandas as pd
import datetime

class Playlists:
    def __init__(self,youtube):
        self.youtube =  youtube
        
    def pull_playlists(self,comments_df):
    
        channel_list = list(set(comments_df['commenter_channel_id']))        
        error=[]
        playlist = []
        count=0
        
        for channelId in channel_list:
            count+=1
            print(count, channelId)
            try:
                request = self.youtube.playlists().list(
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
                            request = self.youtube.playlists().list(
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
        
                
        self.playlist_df = pd.DataFrame(columns=['playlist_id','commenter_channel_id','commenter_channelTitle'])
        
        count = 0
        for p in playlist:
            count+=1
            print(count)
            values = []
            try:
                values.append(p['id'])
                values.append(p['snippet']['channelId'])
                values.append(p['snippet']['channelTitle'])
                self.playlist_df = self.playlist_df.append(pd.Series(values, index=['playlist_id','commenter_channel_id','commenter_channelTitle']),ignore_index=True)
            except:
                pass
        
        return self.playlist_df
        

    
    def get_videos(self, playlist_df):
        
            playlist_list = list(set(self.playlist_df['playlist_id']))
            
            videos = []
            error=[]
            count=0
            
            #get max 50 videos from each playlist
            for playlist in playlist_list:
                count+=1
                print(count, playlist)
                
                try:
                    request = self.youtube.playlistItems().list(
                        part="snippet",
                        maxResults=50,
                        playlistId=playlist
                        )
                    response = request.execute()
                    print (response['pageInfo']['totalResults'])
                    videos.extend(response['items'])
                except:
                    error.append(playlist)
                    print('Rate Limit Exceeded Maybe..')
                    break;
            
            self.videos_df = pd.DataFrame(columns=['video_in_playlist','playlist_channel_id','playlist_channelTitle','video_id','videoTitle','added_to_playlist'])
            
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
                self.videos_df = self.videos_df.append(pd.Series(values, index=['video_in_playlist','playlist_channel_id','playlist_channelTitle','video_id','videoTitle','added_to_playlist']),ignore_index=True)
             
            return self.videos_df



