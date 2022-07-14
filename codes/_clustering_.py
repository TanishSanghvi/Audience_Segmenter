#pip install wordcloud
#pip install matplotlib-venn-wordcloud
#pip install kneed

#pip install https://github.com/sulunemre/word_cloud/releases/download/2/wordcloud-0.post1+gd8241b5-cp38-cp38-macosx_10_9_x86_64.whl
# Alternate - https://candid.technology/error-failed-building-wheel-for-wordcloud/

import re
from copy import deepcopy
import string
import pandas as pd
import nltk
from nltk.corpus import stopwords,words
from nltk.tokenize import word_tokenize 
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from wordcloud import WordCloud, STOPWORDS
from sklearn.feature_extraction.text import TfidfVectorizer
from kneed import KneeLocator
import io
from matplotlib.figure import Figure
import io
import random
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

stop_words = set(stopwords.words('english'))
eng= set(nltk.corpus.words.words())
word_list = set(['para','balas','de','la','en','con','el','la la', 'nan', 'video', 'new', 'best']) #words spoiling the wordcloud

class Clusters():
    
    def __init__(self, df):
        
        self.db_val = df

    def segmentation(self):
    
        def fix(t):
            tokens = word_tokenize(t.lower())
            table = str.maketrans('', '', string.punctuation)
            stripped = [w.translate(table) for w in tokens]
            # remove remaining tokens that are not alphabetic
            only_alpa = [word for word in stripped if word.isalpha()]
            #remove words that are of len 1
            only_alpa = [w for w in only_alpa if len(w)>1]
            # filter out stop words
            only_alpa = [w for w in only_alpa if not w in stop_words]
            #remove words specfic to this
            only_alpa = [w for w in only_alpa if not w in word_list]
            #remove words not in english
            only_alpa = [w for w in only_alpa if w in eng]
        
            text = ' '.join(only_alpa)
            return text
        
        
        self.db_val.rename(columns={'commenter_channel_id':'channel_id'},inplace=True)
        self.db_val=self.db_val[['channel_id','tags']]
        
        self.db_val['tags'] = self.db_val['tags'].astype(str) 
        self.db_val = self.db_val.groupby('channel_id')['tags'].apply(lambda x: ' '.join(x)) #all the tags for a user in one row
        self.db_val = self.db_val.reset_index() 
        self.db_val['tags'] = self.db_val['tags'].apply(lambda t: fix(t)) #Applying the above function
        
        self.db_val2 = self.db_val[self.db_val['tags']!='']
        self.db_val2 = self.db_val2[self.db_val2['tags']!=' ']
        self.db_val2 = self.db_val2[self.db_val2['tags'].notna()].reset_index(drop = True)
        
        a=self.db_val2['tags']
        
        #Running TF-IDF on tags
        v = TfidfVectorizer()
        x = v.fit_transform(a)
        df2 = pd.DataFrame(x.toarray(), columns=v.get_feature_names())
        
        #TFIDF merged with Channel/UserID
        res = pd.concat([self.db_val2, df2], axis=1) 
        res = res.drop(columns=['tags'])
        res = res.set_index('channel_id')
        
        #Clusters present in DataFrame Y
        self.Y=deepcopy(res)
        
        #Applying PCA to get top features
        pca = PCA(n_components = 0.90).fit(self.Y) ###NEED TO SOLVE FOR
        #print(pca.explained_variance_ratio_)
        print(pca.explained_variance_ratio_.cumsum()) #To find how many components explain more than 90% of the variancy 
        pca_d = pca.transform(self.Y)
        
        #Plotting elbow curve to determine number of clusters
        
        Nc = range(1, 6)
        kmeans = [KMeans(n_clusters=i) for i in Nc]
        score = [abs(kmeans[i].fit(pca_d).score(pca_d)) for i in range(len(kmeans))]
        print(Nc, score)
        
        kn = KneeLocator(Nc, score, curve='convex', direction='increasing')
        self.elbow_point = kn.elbow
        
        kmeans=KMeans(n_clusters = self.elbow_point) 
        kmeansoutput=kmeans.fit(pca_d)
        print(kmeansoutput)
        labels = kmeansoutput.labels_
        
        self.Y.insert(0, 'clusters', kmeansoutput.labels_) 

        return labels, Nc, score, pca_d

    def wordcloud(self):

        dd = self.Y.reset_index()
        dd = dd.filter(['channel_id', 'clusters']) #Channel ID and its clusters
        
        df_word_cloud = pd.merge(self.db_val2, dd, on='channel_id') 
        
        clouds = []
        for i in range(self.elbow_point):

            wc = df_word_cloud.loc[df_word_cloud['clusters'] == i]
            wc_unstack=wc.drop('tags', axis=1).join(wc.tags.str.split(expand=True).stack().reset_index(drop=True, level=1).rename('tags'))
            word_string = wc.groupby('clusters')['tags'].apply(' '.join).reset_index()['tags'][0]
            clouds.append(WordCloud(stopwords=STOPWORDS,background_color='white', max_words=40, collocations=False).generate(word_string))
        print('Wc Done')
            # plt.clf()
            # plt.imshow(wordcloud)
            # plt.axis('off')
            # plt.show()

        return clouds
    
    #-----------------------------------------------------------------------------


