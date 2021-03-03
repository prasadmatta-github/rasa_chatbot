import re 
from nltk.corpus import stopwords
from sklearn.metrics.pairwise import linear_kernel
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
# import seaborn as sns

names_data = pd.read_csv('./data/Restaurant_names.csv')
reviews_data = pd.read_csv('./data/Restaurant_reviews.csv')

reviews_data = reviews_data.rename(columns={'Restaurant':'Name'})

dataframe = pd.merge(reviews_data,names_data,how='left',on='Name')
dataframe.drop(['Reviewer','Time','Pictures','Links','Collections'],axis=1, inplace=True)

dataframe['Cost'] = dataframe['Cost'].str.replace(',','').astype(int)

dataframe['Rating'] = dataframe['Rating'].str.replace('Like','1').astype(float)

dataframe['Name'][dataframe['Rating'].isnull() == True].value_counts()

dataframe['Rating'].fillna(4, inplace=True)

# Changing NaN reviews by '-'
dataframe['Review'] = dataframe['Review'].fillna('-')
dataframe.isnull().sum()

dataframe['Metadata'].fillna('0 Review, 0 Follower', inplace=True)

dataframe['Metadata'] = dataframe['Metadata'].str.replace('Reviews','Review') 
dataframe['Metadata'] = dataframe['Metadata'].str.replace('Followers','Follower') 

dataframe['Metadata'][dataframe['Metadata'].str.endswith('w')] = dataframe['Metadata'][dataframe['Metadata'].str.endswith('w')]+', - Follower'
dataframe[['Reviews','Followers']] = dataframe['Metadata'].str.split(',',expand=True)

dataframe['Reviews'] = dataframe['Reviews'].str.replace('Review','')
dataframe['Reviews'] = dataframe['Reviews'].str.replace('Posts','')
dataframe['Reviews'] = dataframe['Reviews'].str.replace('Post','')
dataframe['Followers'] = dataframe['Followers'].str.replace('Follower','')
dataframe['Followers'] = dataframe['Followers'].str.replace('-','0')
dataframe[['Reviews','Followers']] = dataframe[['Reviews','Followers']].astype(int)
dataframe.drop(['Metadata'], axis=1, inplace=True)
dataframe = dataframe.sort_values(['Name', 'Cost'], ascending = False).reset_index()
dataframe.drop('index',axis=1, inplace=True)

restaurants = list(dataframe['Name'].unique())
dataframe['Mean Rating'] = 0
dataframe['Mean Reviews'] = 0
dataframe['Mean Followers'] = 0

for i in range(len(restaurants)):
    dataframe['Mean Rating'][dataframe['Name']==restaurants[i]] = dataframe['Rating'][dataframe['Name']==restaurants[i]].mean()
    dataframe['Mean Reviews'][dataframe['Name']==restaurants[i]] = dataframe['Reviews'][dataframe['Name']==restaurants[i]].mean()
    dataframe['Mean Followers'][dataframe['Name']==restaurants[i]] = dataframe['Followers'][dataframe['Name']==restaurants[i]].mean()

scaler = MinMaxScaler(feature_range = (1,5))
dataframe[['Mean Rating', 'Mean Reviews', 'Mean Followers']] = scaler.fit_transform(dataframe[['Mean Rating','Mean Reviews', 'Mean Followers']]).round(2)

replace_space = re.compile(r'[/(){}\[\]\|@,;]')
remove_symbols = re.compile('[^0-9a-z #+_]')
stopwords = set(stopwords.words('english'))

def text_preprocessing(text):
    text = text.lower()
    
    text = replace_space.sub(' ', text)
    text = remove_symbols.sub(' ',text)
    text = ' '.join(word for word in text.split() if word not in stopwords)
    return text

dataframe['Review'] = dataframe['Review'].apply(text_preprocessing)
dataframe['Cuisines'] = dataframe['Cuisines'].apply(text_preprocessing)

restaurants_names = list(dataframe['Name'].unique())

dataframe_rating = dataframe.drop_duplicates(subset='Name')
dataframe_rating = dataframe_rating.sort_values(by='Mean Rating', ascending=False).head(10)
data_rating = dataframe.copy()
def restaurants_reco():
    return list(data_rating['Name'][dataframe_rating['Mean Rating'].index])

def cuisine_recommendation(name):
    data = list(set(data_rating['Cuisines'][data_rating['Name']==name]))
    # print('data',data)
    if len(data)!=0:
        return '{0} are available'.format(data[0])
    else:
        return 'Currently not availble choose another Restaurant.' 


dataframe_reviews = dataframe.drop_duplicates(subset='Name')
dataframe_reviews = dataframe_reviews.sort_values(by='Mean Reviews', ascending=False).head(10)

# plt.figure(figsize=(7,5))
# sns.barplot(data=dataframe_reviews, x='Mean Reviews', y='Name', palette='RdBu')
# plt.title('Top reviewed Restaurants')

dataframe_followers = dataframe.drop_duplicates(subset='Name')
dataframe_followers = dataframe_followers.sort_values(by='Mean Followers',ascending=False).head(10)

# plt.figure(figsize=(7,5))
# sns.barplot(data=dataframe_followers, x='Mean Followers', y='Name', palette='RdBu')
# plt.title('Most Followed top Restaurants')

def get_top_words(column, top_no_of_words, no_of_word):
    vec = CountVectorizer(ngram_range = no_of_word, stop_words='english')
    bag_of_words = vec.fit_transform(column)
    sum_words = bag_of_words.sum(axis=0)
    words_freq = [(word, sum_words[0, idx]) for word, idx in vec.vocabulary_.items()]
    words_freq = sorted(words_freq, key = lambda x:x[1], reverse = True)
    return words_freq[:top_no_of_words]

list1 = get_top_words(dataframe['Cuisines'], 20,(2,2))

dataframe_words_ = pd.DataFrame(list1, columns=['Words','Count'])

# plt.figure(figsize=(7,6))
# sns.barplot(data=dataframe_words_,x='Count',y='Words')
# plt.title('Word couple frequency for Cuisines')

dataframe.set_index('Name', inplace=True)

indices = pd.Series(dataframe.index)

tfidf = TfidfVectorizer(analyzer='word', ngram_range=(1, 2), min_df=0, stop_words='english')
tfidf_matrix = tfidf.fit_transform(dataframe['Review'])

cosine_similarities = linear_kernel(tfidf_matrix, tfidf_matrix)

def recommend(name, cosine_similarities = cosine_similarities):
    print('check123',name)
    recommend_restaurant = []
    print('checking',indices[indices==name].index[0]   )
    idx = indices[indices==name].index[0]    
    score_series = pd.Series(cosine_similarities[idx]).sort_values(ascending=False)
    top30_indexs = list(score_series.iloc[0:31].index)
    for each in top30_indexs:
        recommend_restaurant.append(list(dataframe.index)[each])
    dataframe_new = pd.DataFrame(columns=['Cuisines','Mean Ratings', 'Cost', 'Timings'])

    for each in recommend_restaurant:
        dataframe_new = dataframe_new.append(pd.DataFrame(dataframe[['Cuisines','Mean Rating','Cost', 'Timings']][dataframe.index==each].sample()))
        
    dataframe_new = dataframe_new.drop_duplicates(subset=['Cuisines','Mean Rating','Cost'], keep=False)
    dataframe_new = dataframe_new.sort_values(by='Mean Rating', ascending=False).head(10)
#     print('top')
#     print(dataframe_new.head())
    return dataframe_new

# print(recommend('Hyderabadi Daawat'))

# print(list(recommend('Hyderabadi Daawat').index))




