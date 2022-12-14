# -*- coding: utf-8 -*-
"""collaborative_filtering.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Wgr0WRWk7_4UCwaeCzsK78XRiuv1Nd4H

## Import Libary dan dataset
"""

import pandas as pd
import numpy as np
import warnings
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import matplotlib.pyplot as plt


warnings.filterwarnings('ignore')

df = pd.read_csv('/content/tourism_rating.csv')
df1 = pd.read_csv('/content/tourism_with_id.csv')

"""## Exploratory Data Analysis

Dataset tourism_rating
"""

# menampilkan 3 overview dataset df secara random
df.sample(3)

# cek dimensi pada dataset df
print("Total Rows: {} dan Cols: {}".format(df.shape[0], df.shape[1]))

# cek informasi dari tiap fitur df
df.info()

# cek total user pada dataset df
len(df['User_Id'].unique())

# cek total place yang diberi rating 
len(df['Place_Id'].unique())

# cek statistika deskripsi dari dataset
df.describe()

"""Dataset tourism_with_id  """

# menampilkan 3 overview dataset df1 secara random
df1.sample(3)

# cek dimensi pada dataset df1
print("Total Rows: {} dan Cols: {}".format(df1.shape[0], df1.shape[1]))

# cek informasi dari tiap fitur df1
df1.info()

# cek total place pada dataset df1
len(df1['Place_Id'].unique())

# cek sebaran kota wisata pada dataset
cols = df1['City'].value_counts()
cols = cols.keys()

import matplotlib.pyplot as plt
plt.bar(x=cols,height=df1['City'].value_counts())
plt.show()

table = pd.crosstab(df1['Category'], df1['City'])
table.plot(kind="bar", figsize=(12,10))

# cek statika deskripsi dari dataset
df1.describe()

"""## Data Cleaning

Dataset tourism_rating
"""

Total = df.isnull().sum().sort_values(ascending=False)          

Percent = (df.isnull().sum()*100/df.isnull().count()).sort_values(ascending=False)   

missing_data = pd.concat([Total, Percent], axis = 1, keys = ['Total', 'Percentage of Missing Values'])    
missing_data

df.duplicated().sum()

df.drop_duplicates(inplace=True)

df.duplicated().sum()

df['Place_Ratings'] = df['Place_Ratings'].astype('float')

"""Dataset tourism_with_id  """

Total = df1.isnull().sum().sort_values(ascending=False)          

Percent = (df1.isnull().sum()*100/df1.isnull().count()).sort_values(ascending=False)   

missing_data = pd.concat([Total, Percent], axis = 1, keys = ['Total', 'Percentage of Missing Values'])    
missing_data

df1.duplicated().sum()

df1.drop(columns=['Coordinate', 'Lat', 'Long', 'Unnamed: 11',
       'Unnamed: 12', 'Time_Minutes', 'Rating', 'Description'], inplace=True)

df = pd.merge(df, df1, on='Place_Id')

df.head()

"""## Preprocessing"""

place_ids = df['Place_Id'].unique().tolist()
user_ids = df['User_Id'].unique().tolist()

# Melakukan encoding userID
user_to_user_encoded = {x: i for i, x in enumerate(user_ids)}
print('encoded userID : ', user_to_user_encoded)
 
# Melakukan proses encoding angka ke ke userID
user_encoded_to_user = {i: x for i, x in enumerate(user_ids)}
print('encoded angka ke userID: ', user_encoded_to_user)

# Melakukan proses encoding placeID
place_to_place_encoded = {x: i for i, x in enumerate(place_ids)}
 
# Melakukan proses encoding angka ke placeID
place_encoded_to_place = {i: x for i, x in enumerate(place_ids)}

# Mapping userID ke dataframe user
df['user'] = df['User_Id'].map(user_to_user_encoded)
 
# Mapping placeID ke dataframe resto
df['place'] = df['Place_Id'].map(place_to_place_encoded)

df.head()

df = df.sample(frac=1, random_state=42)
df

min_rating = min(df['Place_Ratings'])
 
# Nilai maksimal rating
max_rating = max(df['Place_Ratings'])


# Membuat variabel x untuk mencocokkan data user dan resto menjadi satu value
x = df[['User_Id', 'Place_Id']].values
 
# Membuat variabel y untuk membuat rating dari hasil 
y = df['Place_Ratings'].apply(lambda x: (x - min_rating) / (max_rating - min_rating)).values
 
# Membagi menjadi 80% data train dan 20% data validasi
train_indices = int(0.8 * df.shape[0])
x_train, x_val, y_train, y_val = (
    x[:train_indices],
    x[train_indices:],
    y[:train_indices],
    y[train_indices:]
)
 
print(x, y)

"""## Modelling"""

class RecommenderNet(tf.keras.Model):
 
  # Insialisasi fungsi
  def __init__(self, num_users, num_place, embedding_size, **kwargs):
    super(RecommenderNet, self).__init__(**kwargs)
    self.num_users = num_users
    self.num_place = num_place
    self.embedding_size = embedding_size
    self.user_embedding = layers.Embedding( # layer embedding user
        num_users,
        embedding_size,
        embeddings_initializer = 'he_normal',
        embeddings_regularizer = keras.regularizers.l2(1e-6)
    )
    self.user_bias = layers.Embedding(num_users, 1) # layer embedding user bias
    self.place_embedding = layers.Embedding( # layer embeddings resto
        num_place,
        embedding_size,
        embeddings_initializer = 'he_normal',
        embeddings_regularizer = keras.regularizers.l2(1e-6)
    )
    self.place_bias = layers.Embedding(num_place, 1) # layer embedding resto bias
 
  def call(self, inputs):
    user_vector = self.user_embedding(inputs[:,0]) # memanggil layer embedding 1
    user_bias = self.user_bias(inputs[:, 0]) # memanggil layer embedding 2
    place_vector = self.place_embedding(inputs[:, 1]) # memanggil layer embedding 3
    place_bias = self.place_bias(inputs[:, 1]) # memanggil layer embedding 4
 
    dot_user_place = tf.tensordot(user_vector, place_vector, 2) 
 
    x = dot_user_place + user_bias + place_bias
    
    return tf.nn.sigmoid(x) # activation sigmoid

# Mendapatkan jumlah user
num_users = len(df['User_Id'])
print(num_users)
 
# Mendapatkan jumlah resto
num_place = len(df['Place_Id'])
print(num_place)

model = RecommenderNet(num_users, num_place, 100) # inisialisasi model
 
# model compile
model.compile(
    loss = tf.keras.losses.MeanSquaredError(),
    optimizer = keras.optimizers.Adagrad(learning_rate=0.01),
    metrics=[tf.keras.metrics.RootMeanSquaredError()]
)

# Memulai training
 
history = model.fit(
    x = x_train,
    y = y_train,
    batch_size = 24,
    epochs = 10,
    validation_data = (x_val, y_val)
)

"""## Evaluation"""

plt.plot(history.history['root_mean_squared_error'])
plt.plot(history.history['val_root_mean_squared_error'])
plt.title('model_metrics')
plt.ylabel('root_mean_squared_error')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

"""## Testing model"""

place_df = df
df2 = df

# Mengambil sample user
user_id = df2.User_Id.sample(1).iloc[0]
place_visited_by_user = df[df.User_Id == user_id]
place_not_visited = place_df[~place_df['Place_Id'].isin(place_visited_by_user.Place_Id.values)]['Place_Id']

place_visited_by_user['Place_Id'] is place_not_visited

place_not_visited = list(
    set(place_not_visited)
    .intersection(set(place_to_place_encoded.keys()))
)

place_not_visited = [[place_to_place_encoded.get(x)] for x in place_not_visited]
user_encoder = user_to_user_encoded.get(user_id)
user_place_array = np.hstack(
    ([[user_encoder]] * len(place_not_visited), place_not_visited)
)

ratings = model.predict(user_place_array).flatten()

top_ratings_indices = ratings.argsort()[-10:][::-1]
recommended_place_ids = [
    place_encoded_to_place.get(place_not_visited[x][0]) for x in top_ratings_indices
]

place_visited_by_user.sort_values(
        by = 'Place_Ratings',
        ascending=False
    )

print('Showing recommendations for users: {}'.format(user_id))
print('===' * 9)
print('Place with high ratings from user')
print('----' * 8)

top_place_user = (
    place_visited_by_user.sort_values(
        by = 'Place_Ratings',
        ascending=False
    )
    .head(5)
    .Place_Id.values
)

place_df_rows = place_df[place_df['Place_Id'].isin(top_place_user)].drop_duplicates(subset=['Place_Id'])
for row in place_df_rows.itertuples():
    print(row.Place_Name, ':', row.City)

print('----' * 8)
print('Top 10 place recommendation')
print('----' * 8)

recommended_place = place_df[place_df['Place_Id'].isin(recommended_place_ids)].drop_duplicates(subset=['Place_Id'])
for row in recommended_place.itertuples():
    print(row.Place_Name, ':', row.City)