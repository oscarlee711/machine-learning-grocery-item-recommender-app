import mysql.connector
from mysql.connector import errorcode
import pandas as pd
import time
from discountme_recommender_helper import *

def compute_similarity_items(all_items, item_id, item_name):
    """ Return the cosine similarity between an item and all items. 
        Args:
            all_items: all items on the database
            item_id: target item id  
            item_name: target item name  
        Returns:
            df_all_items_similarity_scores: data frame store cosine_similarity with all items   
    """
    df_all_items_similarity_scores = pd.DataFrame(
        columns=['ITEM1_ID', 'ITEM2_ID', 'SIM'])
    
    for idx1 in all_items.index:    
        sim = compute_similarity_two_items(
            all_items['ITEM_NAME'][idx1], item_name)
        #add only 
        if sim >= 0.3 and all_items['ITEM_ID'][idx1] != item_id: 
            data_row = [item_id, all_items['ITEM_ID'][idx1], sim]
            df_all_items_similarity_scores.loc[df_all_items_similarity_scores.size] = data_row
        

    return df_all_items_similarity_scores  

def callculate_user_recommendations_online_content_based(count):
    """Find user item recommendations based on item names similirities.  
    Args:
        count: max number of recommnded items
    Returns: None
    """
    try:
      #delete current recomndations from the TEMP table
      reset_recommendation_table()
      #wait for 5 seconds
      time.sleep(5)  # Sleep for 3 seconds

      df_all_transactions = get_all_transactions_db()
      #rank user items
      df_ranked = rank_data(df_all_transactions)
      # get all items
      df_all_items = get_all_items()      
      #compute similarity between all items and user items
      similarity_index_dict = {}

      # get users
      user_ids = df_ranked['user_id'].unique()

      for user_id in user_ids:
        #get user items 
        user_items = df_ranked[df_ranked['user_id'] == user_id]['ITEM_ID']
        df_all_items_similarity_scores = pd.DataFrame(
            columns=['ITEM1_ID', 'ITEM2_ID', 'SIM'])
        
        for item_id in user_items: 
            item_name = df_all_items[df_all_items['ITEM_ID']
                                     == item_id]['ITEM_NAME'].values[0]
            #check in sim dict
            if item_id not in similarity_index_dict.keys():
                df_item_similarity_scores = get_item_sim_scores(item_id=item_id) 
                if len(df_item_similarity_scores) == 0:
                    df_item_similarity_scores = compute_similarity_items(df_all_items, item_id, item_name)  
                    #print(f'Number of sim items with {item_id} > 0.3 is {len(df_item_similarity_scores)}')  
                    #update the Db
                    item_scores_rows = []
                    for idx in df_item_similarity_scores.index:
                        item_scores_rows.append([str(df_item_similarity_scores['ITEM1_ID'][idx]),
                                        str(df_item_similarity_scores['ITEM2_ID'][idx]),
                                        str(df_item_similarity_scores['SIM'][idx] * 100)])
                                       
                    insert_item_sims_db(item_scores_rows) 
                                  

                df_all_items_similarity_scores = pd.concat([df_all_items_similarity_scores, df_item_similarity_scores])                    
                similarity_index_dict[item_id] = df_item_similarity_scores
                    #update the Db          
            else:               
                df_all_items_similarity_scores = pd.concat([df_all_items_similarity_scores,  similarity_index_dict[item_id]]) 
 
       
        #print(f'Number of sim items with {item_id} > 0.3 is {len(similarity_index_dict[item_id])}')  
        user_items = df_ranked[df_ranked['user_id'] == user_id]

        #merge similarity scores with user ranked items
        df_merged = pd.merge(
            left=user_items, right=df_all_items_similarity_scores, left_on='ITEM_ID', right_on='ITEM1_ID')
        
        # compute score based on rank and sim
        df_merged['SCORE'] = df_merged['rank'] * df_merged['SIM']
        df_user_item_scores = df_merged[[
            'user_id', 'comp_id', 'ITEM2_ID', 'SCORE']]
        df_user_item_scores.columns = [
            'USER_ID', 'COM_ID', 'ITEM_ID', 'SCORE']
        count = min(count, len(df_user_item_scores))

        #get top scores 
        df_user_item_top_scores = df_user_item_scores.sort_values(
            'SCORE', ascending=False).head(count) 
 
        attrRows = []
        for idx in df_user_item_top_scores.index:
            attrRows.append([str(df_user_item_top_scores['USER_ID'][idx]),
                            str(df_user_item_top_scores['ITEM_ID'][idx]),
                            str(df_user_item_top_scores['COM_ID'][idx]),
                            str(int(df_user_item_top_scores['SCORE'][idx]/10.0))])

        # add user recommedned items        
        insert_user_recommendations_db(attrRows)
        time.sleep(3)  # Sleep for 3 seconds

    except mysql.connector.Error as err:
      if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
      elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
      else:
        print(err)



#callculate_user_recommendations_online_content_based(10)

# Example test set (dictionary of user-item ratings)
test_set = {
    'User1': [10, 15, 20],
    'User2': [5, 10, 25],
    'User3': [10, 15, 30],
}

# Example recommendations (dictionary of user-recommended items)
recommendations = {
    'User1': [5, 10, 15, 20, 25],
    'User2': [10, 15, 20, 25, 30],
    'User3': [5, 10, 15, 20, 25],
}

precision, recall = evaluate_cbrs(test_set, recommendations)
print(f"Average Precision: {precision}")
print(f"Average Recall: {recall}")


