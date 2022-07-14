import pandas as pd

class YoutubeComments:
    
    def __init__(self,youtube,videos_list,directory=''):
    
        self.youtube = youtube
        self.directory = directory
        self.videos = videos_list
            
    def get_comments(self):
                
        comments = []
        error=[]
        df = pd.DataFrame(columns=['video_id','comment_id','commenter_Name','commenter_channel_id'])
        
        #get the 1st 100 comments
        print('Extracting comments..')
        count=0
        for videoId in self.videos:
            count+=1
            print(count, videoId)
            try:
                request = self.youtube.commentThreads().list(
                    part="snippet,replies",
                    maxResults=100,
                    videoId=videoId
                )
                response = request.execute()
                comments.extend(response['items'])
            except:
                error.append(videoId)
        #return pd.DataFrame(error)  
        
        print('Extracting replies..')
        for c in comments:

            values = []
            values.append(c['snippet']['topLevelComment']['snippet']['videoId'])
            values.append(c['snippet']['topLevelComment']['id'])
            values.append(c['snippet']['topLevelComment']['snippet']['authorDisplayName'])
            try:
                values.append(c['snippet']['topLevelComment']['snippet']['authorChannelId']['value'])
            except:
                values.append('')
            df = df.append(pd.Series(values, index=['video_id','comment_id','commenter_Name','commenter_channel_id']),ignore_index=True)
        
        for c in comments:
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
                pass

        print('Comments and Replies Extracted..')        
    
        return df
    
  
    
    