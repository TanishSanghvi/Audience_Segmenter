import googleapiclient.discovery
import os

class YoutubeAuthentication():

    def __init__(self,developer_key):

        self.developer_key = developer_key
     #   self.directory =directory
    
    def connect_google_api(self):
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"         
        api_service_name = "youtube"
        api_version = "v3"
        DEVELOPER_KEY = self.developer_key
        youtube = googleapiclient.discovery.build(
                    api_service_name, api_version, developerKey = DEVELOPER_KEY)
        def verify_developer_key(youtube):
            test_video_id='jNQXAC9IVRw' ## first video on yt
            request = youtube.videos().list(
                    part="snippet,contentDetails,statistics",
                    id=test_video_id)
            request.execute()
        verify_developer_key(youtube)
        return youtube
    