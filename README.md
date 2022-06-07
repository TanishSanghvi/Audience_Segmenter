# User-Hack

## ABOUT

- The goal of the project is to ‘hack’ user data and separate them into different groups or segments based on shared characteristics. 
- Companies can profit from knowing their customer segments as they can then create contextualized advertisements or enhance their digital engagements based on the ‘taste’ of their users
- In the following project we have created a blueprint of this process by utilizing YouTube data and it’s API which provides various metrics about a user such as their playlists, videos, commenters and so on
- Post this, data processing, NLP processes (TF_IDF, N-grams) and clustering modules (K-means, Elbow Curves, Silhouette Scores) were applied to generate insightful wordclouds


## BUILT WITH / MODULES USED

Built with Python 3.7. Modules used:
 - GoogleAPIClient
 - NLTK
 - KMeans
 - PCA
 - TF-IDF
 - Silhouette_Score
 - Elbow_Curve

## SUMMARIZED WORKFLOW

- Get a list of videos (video_ids) belonging to a particular industry (music, travel, finance etc)
- Pull the list of commenters on these videos
- Pull the list of playlist ID’s belonging to these users
- Pull the list of videos belonging to these playlists
- Pull the ‘tags’ belonging to each video (YouTube has tags for each video)
- Use NLP techniques to clean these tags followed by K-means in order to cluster the users based on their preferences (‘tags’)


## DETAILS AND RESULTS

- We decided to look for a list of videos specific to a certain domain. We found such a data set on Kaggle which had 2607 video ID’s from various categories such as science, food, history etc. For our use case, we decided to choose ‘Travel’ as the dataset had the most videos (559) from this category
- Post this we followed the rest of the steps in 'Summarized Workflow' as mentioned above

- Following is the Elbow Curve we got on running our model: 

  <img width="268" alt="image" src="https://user-images.githubusercontent.com/69982245/172291120-c2f2efe6-2c8c-40ee-a33d-1e424b2c6e49.png">

- It is clear that the optimum number of clusters are 3. As such we ran KMeans with 3 clusters and plotted our clustered users using matplotlib

  <img width="274" alt="image" src="https://user-images.githubusercontent.com/69982245/172291203-cffa9c6c-551c-473b-b28b-838e66ae0b26.png">

- As one can see, the clusters are very well defined and separable. Based on this, we created wordclouds for each segment based off their video 'tags'. Following are the 3 wordclouds:

  <img width="213" alt="image" src="https://user-images.githubusercontent.com/69982245/172291357-e8795d75-6ce3-464f-9b88-5edfbadb51ee.png">. <img width="213" alt="image" src="https://user-images.githubusercontent.com/69982245/172291370-4fe0e8af-0a8b-477f-9d69-df61e70a07f3.png">. <img width="214" alt="image" src="https://user-images.githubusercontent.com/69982245/172291378-74493106-72a0-4a1f-acad-c7390db8cdd3.png">

- A close look at the wordclouds tells us that the 1st segmented group is interested in videos around travel, tourism, adventures and similar things. The 2nd segmented group in music-related videos. The 3rd segment is interested in gaming and tutorial-based videos predominantly.


## USE CASES
 - This can be an essential asset for a majority of companies who are often concerned with getting relevant insights about their target audience
 - This also has further application as it can be used for strategic profiling of the consumers for subsequent personalised advertisements
 - The project is also in progress to be developed as Web GUI. Further updates coming soon!
