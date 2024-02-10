import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from pathlib import Path
import matplotlib.pyplot as plt
from keras.utils import plot_model

import mysql.connector as msql
from mysql.connector import Error

try:
    # Connect to DiscountMate Database

    conn = msql.connect(host='34.129.54.95',
                        user='oscar',
                        password='p@ssword0501')

    cursor = conn.cursor()
    print("Database is connected")
    cursor.execute("use dcmdb")
    print("Connected to dcmdb")

    # Truncate ITEM_RATING table before recalculating item rating

    cursor.execute("TRUNCATE TABLE ITEM_RATING")
    conn.commit()
    print("All records in ITEM_RATING table are deleted")

    # Recalculating ITEM_RATING table by the latest USER_ORDER records

    cursor.execute('''
      INSERT INTO ITEM_RATING 
      SELECT 
      USER_ID,
      ITEM_ID,
      SUM(ORDER_ITEM_QTY) AS RATING
      FROM USER_ORDER A 
      INNER JOIN ORDER_ITEM B
      ON A.ORDER_ID = B.ORDER_ID
      GROUP BY USER_ID, ITEM_ID
      ORDER BY USER_ID, ITEM_ID
      ''')
    conn.commit()
    print("ITEM_RATING table is reloaded")

    # Retrieve recalculated item rating result from database

    SQL_Query = pd.read_sql_query('''
      SELECT 
      USER_ID,
      ITEM_ID,
      RATING
      FROM ITEM_RATING
    ''', conn)
    df = pd.DataFrame(SQL_Query)

    # Preprocessing Data
    # Encode users and movies as integer indices

    # Get a list of User_Id
    user_ids = df["USER_ID"].unique().tolist()

    # Assign sequential number to every User_Id for indexing
    user2user_encoded = {x: i for i, x in enumerate(user_ids)}

    # For each index number assign the corresponding User_Id
    userencoded2user = {i: x for i, x in enumerate(user_ids)}

    # Get a list of Item_Id
    item_ids = df["ITEM_ID"].unique().tolist()

    # Assign sequential number to every Item_Id for indexing
    item2item_encoded = {x: i for i, x in enumerate(item_ids)}

    # For each index number assign the corresponding Item_Id
    item_encoded2item = {i: x for i, x in enumerate(item_ids)}

    # Create new columns for user_encoded and item_encoded
    df["user"] = df["USER_ID"].map(user2user_encoded)
    df["item"] = df["ITEM_ID"].map(item2item_encoded)

    num_users = len(user2user_encoded)
    num_items = len(item_encoded2item)
    df["rating"] = df["RATING"].values.astype(np.float32)

    # min and max ratings will be used to normalize the ratings later
    min_rating = min(df["rating"])
    max_rating = max(df["rating"])

    print(
        "Number of users: {}, Number of Items: {}, Min rating: {}, Max rating: {}".format(
            num_users, num_items, min_rating, max_rating
        )
    )

    # Prepare training and validation data

    # Selects all rows from the DataFrame df in a random order
    # Using a random seed of 42 to ensure the same order is obtained each time the code is run
    df = df.sample(frac=1, random_state=42)

    # Create an array for user with item
    x = df[["user", "item"]].values

    # Normalize the targets between 0 and 1. Makes it easy to train.
    y = df["rating"].apply(lambda x: (x - min_rating) / (max_rating - min_rating)).values

    # Assuming training on 90% of the data and validating on 10%.
    train_indices = int(0.9 * df.shape[0])

    # x_train = user, item. y_train = rating
    x_train, x_val, y_train, y_val = (
        x[:train_indices],
        x[train_indices:],
        y[:train_indices],
        y[train_indices:],
    )

    # Create the model with embedding layer
    # Embedding layer is a layer specifically designed to learn and represent categorical or discrete input data in a continuous vector space.
    # It is used for text where each word or token is mapped to a dense vector representation, known as an embedding.
    # The embedding layer allows the model to learn meaningful representations that capture similarities and relationships between different categories.

    # Embed both users and items in to 50-dimensional vectors.
    # The model computes a match score between user and movie embeddings via a dot product, and adds a per-item and per-user bias.
    # The match score is scaled to the [0, 1] interval via a sigmoid, as our ratings are normalized to this range.

    EMBEDDING_SIZE = 50

    class discountmateRecommender(keras.Model):
        def __init__(self, num_users, num_items, embedding_size, **kwargs):
            super().__init__(**kwargs)
            self.num_users = num_users
            self.num_items = num_items
            self.embedding_size = embedding_size
            self.user_embedding = layers.Embedding(
                num_users,
                embedding_size,
                embeddings_initializer="he_normal",
                embeddings_regularizer=keras.regularizers.l2(1e-6),
            )
            self.user_bias = layers.Embedding(num_users, 1)
            self.item_embedding = layers.Embedding(
                num_items,
                embedding_size,
                embeddings_initializer="he_normal",
                embeddings_regularizer=keras.regularizers.l2(1e-6),
            )
            self.item_bias = layers.Embedding(num_items, 1)

        def call(self, inputs):
            user_vector = self.user_embedding(inputs[:, 0])
            user_bias = self.user_bias(inputs[:, 0])
            item_vector = self.item_embedding(inputs[:, 1])
            item_bias = self.item_bias(inputs[:, 1])
            dot_user_item = tf.tensordot(user_vector, item_vector, 2)
            # Add all the components (including bias)
            x = dot_user_item + user_bias + item_bias
            # The sigmoid activation forces the rating to between 0 and 1
            return tf.nn.sigmoid(x)

    model = discountmateRecommender(num_users, num_items, EMBEDDING_SIZE)
    model.compile(
        loss=tf.keras.losses.BinaryCrossentropy(),
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
    )

    # Train the model based on the data split

    history = model.fit(
        x=x_train,  # user and movie
        y=y_train,  # rating
        batch_size=64,
        epochs=5,
        verbose=1,
        validation_data=(x_val, y_val),
    )

    # Retrieve ITEM data from DiscountMate Database

    Load_Item_SQL_Query = pd.read_sql_query('''
      SELECT 
      A.ITEM_ID,
      A.ITEM_NAME,
      B.CAT_NAME
      FROM ITEM A
      LEFT JOIN CATEGORY B
      ON A.CAT_ID = B.CAT_ID
    ''', conn)
    item_df = pd.DataFrame(Load_Item_SQL_Query)

    # Truncate RECOMMEND_ITEM_COLLAB_FILTER table for delete insert

    cursor.execute("TRUNCATE TABLE RECOMMEND_ITEM_COLLAB_FILTER")
    conn.commit()
    print("All records in RECOMMEND_ITEM_COLLAB_FILTER table are deleted")

    # Insert system recommendations result to DiscountMate database RECOMMEND_ITEM_COLLAB_FILTER table

    for index, row in df.iterrows():
        user_id = row['USER_ID']
        items_watched_by_user = df[df.USER_ID == user_id]
        items_not_bought = item_df[
            ~item_df["ITEM_ID"].isin(items_watched_by_user.ITEM_ID.values)
        ]["ITEM_ID"]
        items_not_bought = list(
            set(items_not_bought).intersection(set(item2item_encoded.keys()))
        )
        items_not_bought = [[item2item_encoded.get(x)] for x in items_not_bought]
        user_encoder = user2user_encoded.get(user_id)
        user_item_array = np.hstack(
            ([[user_encoder]] * len(items_not_bought), items_not_bought)
        )
        ratings = model.predict(user_item_array).flatten()
        top_ratings_indices = ratings.argsort()[-10:][::-1]
        recommended_item_ids = [
            item_encoded2item.get(items_not_bought[x][0]) for x in top_ratings_indices
        ]

        recommended_items = item_df[item_df["ITEM_ID"].isin(recommended_item_ids)]
        for row in recommended_items.itertuples():
            print(user_id, " : ", row.ITEM_NAME, ":", row.CAT_NAME)
            RCM_USER_ID = str(user_id)
            RCM_ITEM_ID = str(row.ITEM_ID)
            cursor.execute("""
                          INSERT INTO RECOMMEND_ITEM_COLLAB_FILTER (
                          RCM_USER_ID,
                          RCM_ITEM_ID,
                          RCM_COM_ID,
                          RCM_INSERT_DATE
                          )
                          VALUES (
                          """ + RCM_USER_ID + """,
                          """ + RCM_ITEM_ID + """,
                          1,
                          CURDATE()                     
                          )
                          """)
            print("Insert into RECOMMEND_ITEM_COLLAB_FILTER. USER_ID: " + RCM_USER_ID + " | ITEM_ID: " + RCM_ITEM_ID)
            conn.commit()

    conn.close()
    print('Closed connection to DiscountMate database')

except Error as e:
    print("Error with connection", e)

