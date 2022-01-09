
#pip install wordcloud
#pip install matplotlib-venn-wordcloud
import re
from copy import deepcopy
import string
import psycopg2
import pylab as pl
import pandas as pd
import nltk
from nltk.corpus import stopwords,words
from nltk.tokenize import word_tokenize 
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from wordcloud import WordCloud, STOPWORDS
from sklearn.metrics import silhouette_score
from matplotlib_venn_wordcloud import venn2_wordcloud, venn3_wordcloud
from sklearn.feature_extraction.text import TfidfVectorizer

stop_words = set(stopwords.words('english'))
eng= set(nltk.corpus.words.words())
word_list = set(['para','balas','de','la','en','con','el','la la', 'nan', 'video', 'new', 'best']) #words spoiling the wordcloud

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


db_val = pd.read_csv('travel_data_with_tags.csv')
db_val.rename(columns={'commenter_channel_id':'channel_id'},inplace=True)
db_val=db_val[['channel_id','tags']]

db_val['tags'] = db_val['tags'].astype(str) 
db_val = db_val.groupby('channel_id')['tags'].apply(lambda x: ' '.join(x)) #all the tags for a user in one row
db_val = db_val.reset_index() 
db_val['tags'] = db_val2['tags'].apply(lambda t: fix(t)) #Applying the above function

db_val2 = db_val[db_val['tags']!='']
db_val2 = db_val2[db_val2['tags']!=' ']
db_val2 = db_val2[db_val2['tags'].notna()].reset_index(drop = True)

a=db_val2['tags']

#Running TF-IDF on tags
v = TfidfVectorizer()
x = v.fit_transform(a)
df2 = pd.DataFrame(x.toarray(), columns=v.get_feature_names())

#TFIDF merged with Channel/UserID
res = pd.concat([db_val2, df2], axis=1) 
res = res.drop(columns=['tags'])
res = res.set_index('channel_id')

#Clusters present in DataFrame Y
Y=deepcopy(res)

#Applying PCA to get top features
pca = PCA(n_components = 1500).fit(Y)
#print(pca.explained_variance_ratio_)
print(pca.explained_variance_ratio_.cumsum()) #To find how many components explain more than 90% of the variancy 
pca_d = pca.transform(Y)

#Plotting elbow curve to determine number of clusters
Nc = range(1, 10)
kmeans = [KMeans(n_clusters=i) for i in Nc]
score = [abs(kmeans[i].fit(pca_d).score(pca_d)) for i in range(len(kmeans))]
pl.plot(Nc,score)
pl.xlabel('Number of Clusters')
pl.ylabel('Score')
pl.title('Elbow Curve')
pl.show()

#Based on elbow curve
kmeans=KMeans(n_clusters=3) 
kmeansoutput=kmeans.fit(pca_d)
Y.insert(0, 'clusters', kmeansoutput.labels_) 
pl.figure('3 Cluster K-Means')

pl.scatter(pca_d[:, 0], pca_d[:, 1], c=kmeansoutput.labels_)
pl.xlabel('')
pl.ylabel('')
pl.title('3 Cluster K-Means')
pl.show()

#-----------------------------------------------------------------------------

dd = Y.reset_index()
dd = dd.filter(['channel_id', 'clusters']) #Channel ID and its clusters
dd.to_csv('clusters_formed.csv')

d_0 = dd.loc[dd['clusters'] == 0]
d_1 = dd.loc[dd['clusters'] == 1]
d_2 = dd.loc[dd['clusters'] == 2]


d_0.to_excel('cluster0.xlsx')
d_1.to_excel('cluster1.xlsx')
d_2.to_excel('cluster2.xlsx')

#------------------------------------------------------------------------------
## VISUALIZATIONS

#User, tags and clustr they belong to
df_word_cloud = pd.merge(db_val2, dd, on='channel_id') 

wc_0 = df_word_cloud.loc[df_word_cloud['clusters'] == 0]
wc_1 = df_word_cloud.loc[df_word_cloud['clusters'] == 1]
wc_2 = df_word_cloud.loc[df_word_cloud['clusters'] == 2]

wc_0.to_excel('cluster0_tags.xlsx')
wc_1.to_excel('cluster1_tags.xlsx')
wc_2.to_excel('cluster2_tags.xlsx')

wc_0_unstack=wc_0.drop('tags', axis=1).join(wc_0.tags.str.split(expand=True).stack().reset_index(drop=True, level=1).rename('tags'))
wc_1_unstack=wc_1.drop('tags', axis=1).join(wc_1.tags.str.split(expand=True).stack().reset_index(drop=True, level=1).rename('tags'))
wc_2_unstack=wc_2.drop('tags', axis=1).join(wc_2.tags.str.split(expand=True).stack().reset_index(drop=True, level=1).rename('tags'))

#string of tags
word_string0 = wc_0.groupby('clusters')['tags'].apply(' '.join).reset_index()['tags'][0] #Creating one string with all the tags that belong to a cluster
word_string1 = wc_1.groupby('clusters')['tags'].apply(' '.join).reset_index()['tags'][0]
word_string2 = wc_2.groupby('clusters')['tags'].apply(' '.join).reset_index()['tags'][0]

#make word cloud
wordcloud0 = WordCloud(stopwords=STOPWORDS,background_color='white', max_words=40, collocations=False).generate(word_string0)
wordcloud1 = WordCloud(stopwords=STOPWORDS,background_color='white', max_words=40, collocations=False).generate(word_string1)
wordcloud2 = WordCloud(stopwords=STOPWORDS,background_color='white', max_words=40, collocations=False).generate(word_string2)

plt.clf()
plt.imshow(wordcloud0)
plt.axis('off')
plt.show()

plt.clf()
plt.imshow(wordcloud1)
plt.axis('off')
plt.show()

plt.clf()
plt.imshow(wordcloud2)
plt.axis('off')
plt.show()

