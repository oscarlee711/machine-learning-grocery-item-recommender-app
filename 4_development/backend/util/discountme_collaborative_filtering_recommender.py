
import mysql.connector
from mysql.connector import errorcode
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import time
from discountme_recommender_helper import *

def callculate_user_recommendations_online_collaborative_filtering(count):
    """Find user item recommendations and update the db. 
    Args:
        count: max number of recommnded items 
    Returns: None      
    """
    try:
      # connect to DB and get all transactions 
      df = get_all_transactions_db(cnx)
      cnx.close()

      # scale the data 
      scaler = StandardScaler()      
      df_scaled = pd.DataFrame(scaler.fit_transform(df[['DPCT', 't_count', 'days']]), index = df.index, columns=['DPCT', 't_count', 'days']) 
      # Paramters to consider to match items are: 
      # days: differnce between transaction date and today in number of days.
      # DPCT: Discount percentage   
      # t_count: transaction count  
      # Step 1: compute similarity and create a dataframe 
      item_sim = cosine_similarity(df_scaled)  
      df_item_sim = pd.DataFrame(item_sim, index = df['ITEM_ID'], columns=df['ITEM_ID'])  

      # Step 2: find recommndations for users 
      # get all users 
      users = df['user_id'].unique()
      # get transactions per user 
      df_grouped = df.groupby(['user_id', 'ITEM_ID', 'comp_id']).max()
      df_grouped.reset_index(inplace = True)

      #delete current recomndations  
      reset_recommendation_table()
      #wait for 5 seconds
      time.sleep(5) # Sleep for 3 seconds

      for user in users:
        # get items within past month. 
        user_items = df_grouped[(df_grouped['user_id'] == user) & (df_grouped['days'] > 30) ].sort_values(['t_date'], ascending= False)['ITEM_ID'].unique()

        similiarity_scores = df_item_sim [user_items].mean(axis = 1).sort_values(ascending = False)
        count = min(len(similiarity_scores), count)
        similiarity_scores_top_10 = similiarity_scores[:count]
        attrRows = []
        for u_item in similiarity_scores_top_10.index:
            comp_id = df[df['ITEM_ID'] == u_item]['comp_id'].unique()[0]
            attrRows.append((str(user),str(u_item),str(comp_id))) 
       
        # add user recommedned items 
        #insert_user_recommendations_db(attrRows)
        time.sleep(1) # Sleep for 3 seconds
    except mysql.connector.Error as err:
      if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
      elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
      else:
        print(err)  