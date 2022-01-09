
pip install nltk
import pandas as pd
import re
import nltk
from nltk.util import ngrams
from nltk.corpus import stopwords
nltk.download('stopwords')
nltk.download('punkt')
stop = set(stopwords.words('english'))


df_tags = pd.read_excel('travel_video_tags_ytapi.xlsx')

df = df_tags[['video_id','tags']]
df['tags'] = df['tags'].map(lambda x: x[1:-1]) #remove the [] from the tags
df = df.assign(tags=df.tags.str.split(",")).explode('tags') #put each tag on a diff line
df['tags'] = df['tags'].map(lambda x: x.strip()[1:-1]) #remove the space and quotes from tags
df_video_unique_tags = df.drop_duplicates()

df_commenter_playlist = pd.read_excel('travel_playlists.xlsx')
df_commenter_playlist.rename(columns={'commenter_channelTitle':'commenter'},inplace=True)
df_commenter_playlist = df_commenter_playlist[['commenter','commenter_channel_id','playlist_id']]

df_playlist_video = pd.read_excel('travel_all_videos.xlsx')
df_playlist_video.rename(columns={'video_in_playlist':'playlist_id'},inplace=True)
df_playlist_video = df_playlist_video[['playlist_id','video_id','videoTitle','added_to_playlist','playlist_channel_id','playlist_channelTitle']]

df_commenter_with_videos_in_playlist = pd.merge(df_commenter_playlist, df_playlist_video, on='playlist_id', how='outer')
df_commenter_with_videos_in_playlist.drop(columns=['playlist_channel_id','playlist_channelTitle'],inplace=True)

df_commenter_with_tags_for_videos = pd.merge(df_commenter_with_videos_in_playlist, df_video_unique_tags, on='video_id', how='left')
commenters_with_tags = df_commenter_with_tags_for_videos.dropna(subset=['tags'])
commenters_with_tags.reset_index(inplace=True)

commenters_with_tags.to_csv('travel_data_with_tags.csv', encoding = 'utf-8', index=False)