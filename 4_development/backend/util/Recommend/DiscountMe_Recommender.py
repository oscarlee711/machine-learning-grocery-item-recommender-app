import mysql.connector
from mysql.connector import errorcode
import pandas as pd
from datetime import date
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import time


#DB config
config = {
    'user': 'mohamed',
    'password': 'p@ssword0503',
    'host': '34.129.54.95',
    'database': 'dcmdb',
    'raise_on_warnings': True
}


def date_group_handler(d):
    """Find a dfference in days between a date and today.
    Args:
        d: a transaction date.
    Returns:
        the number of days.
    """
    date = pd.Timestamp(d)
    today = pd.Timestamp(date.today())
    return (today - date).days


def get_all_transactions_db(cnx):
    """Return all transactions from a db.

    Args:
        cnx: database connection.
    Returns:
        df: a dataframe contains all transaction and for each:
        ITEM_ID: Item ID
        user_id: User ID
        t_date: Transaction date:
        comp_id: Company ID
        t_count: transaction count
        avg_price: average item price
        CP: Current item price
        DP: Discounted item price
        days: differnce between transaction date and today in number of days.
        DPCT: Discount percentage
    """
    query = "SELECT uo.USER_ID user_id,  o.ITEM_ID, c.COM_ID comp_id, max(STR_TO_DATE(t.TXN_DATE, '%d/%m/%Y')) t_max_date, min(STR_TO_DATE(t.TXN_DATE, '%d/%m/%Y')) t_min_date,"
    query += " i.ITEM_NAME, count(uo.USER_ID) num_items,"
    query += " avg(o.ORDER_ITEM_BASE_PRICE) avg_price, sum(o.ORDER_ITEM_QTY) sum_qnt, avg(cp.IP_ITEM_BASE_PRICE) CP,"
    query += " avg(cp.IP_ITEM_DISCOUNT_PRICE) DP, MAX(cp.IP_FOUR_WK_HIGHEST_PRICE) MAXP, MIN(cp.IP_FOUR_WK_LOWEST_PRICE) MINP"
    query += " FROM dcmdb.ORDER_ITEM o inner join USER_ORDER uo on uo.ORDER_ID = o.ORDER_ID"
    query += " inner join ITEM i on o.ITEM_ID = i.ITEM_ID inner join STG_TRANSACTION t on t.TXN_INVOICE_NUM = o.ORDER_ID"
    query += " inner join ITEM_PRICE_CURRENT cp on cp.ITEM_ID = i.ITEM_ID inner join STORE s on s.STORE_ID = uo.STORE_ID"
    query += " inner join COMPANY c on c.COM_ID = s.COM_ID"
    query += " where t.TXN_ITEM_DESC = i.ITEM_NAME"
    query += " group by uo.USER_ID, c.COM_ID, o.ITEM_ID, i.ITEM_NAME order by uo.USER_ID"

    df = pd.read_sql(sql=query, con=cnx, parse_dates=["t_date"])
    df = df[['ITEM_ID', 'user_id', 'comp_id', 'num_items',
             'avg_price', 'CP', 'DP', 't_max_date', 't_min_date']]
    df['DP'] = df['DP'].fillna(0)
    df['DPCT'] = 0
    has_discount = df['DP'] <= 0
    df.loc[has_discount, 'DP'] = 0
    df['DPCT'] = pd.to_numeric(df['DP'] / df['CP'])
    df['days'] = df['t_max_date'].apply(date_group_handler)
    return df


def reset_recomndation_table():
    """Delete current recommendations.
    Args: None
    Returns: None
    """
    # connect to DB
    cnx = mysql.connector.connect(**config)
    # preparing a cursor object
    cursorObject = cnx.cursor()
    # deleting data from the RECOMMEND_ITEM table
    query = "DELETE FROM RECOMMEND_ITEM_TEMP"
    cursorObject.execute(query)

    # data deleted
    cnx.commit()
    cnx.close()


def insert_user_recommendations_db(attrRows):
    """Update recomndation table.
    Args:
        df: dataframe contains recpmndation records
    Returns: None
    """
    # connect to DB
    cnx = mysql.connector.connect(**config)
    # preparing a cursor object
    cursorObject = cnx.cursor(prepared=True)
    # inserting data into the RECOMMEND_ITEM table
    query = """INSERT INTO RECOMMEND_ITEM_TEMP
              VALUES (%s, %s, %s, %s)"""
    for attrValues in attrRows:
        try:
            cursorObject.execute(query, attrValues)
        except:
            pass

    # data inserted
    cnx.commit()
    cnx.close()


def insert_item_sims_db(attrRows):
    """Update item sim table.
    Args:
        df: dataframe contains item sim records
    Returns: None
    """
    # connect to DB
    cnx = mysql.connector.connect(**config)
    # preparing a cursor object
    cursorObject = cnx.cursor(prepared=True)
    # inserting data into the RECOMMEND_ITEM table
    query = """INSERT INTO dcmdb.ITEM_SIM
              VALUES (%s, %s, %s)"""
    for attrValues in attrRows:
        try:
            cursorObject.execute(query, attrValues)
        except:
            pass

    # data inserted
    cnx.commit()
    cnx.close()

    


# work for Content-based filtering approch starts here  
def get_all_items(cnx):
    """ Return all items from a db.
        Args:
            cnx: database connection.
        Returns:
            df: a dataframe contains all items
    """
    query = "SELECT i.ITEM_ID, i.ITEM_NAME from ITEM i"
    df_all_items = pd.read_sql(sql=query, con=cnx)
    return df_all_items


def _compute_similarity_two_items(item1, item2):
    """ Return the cosine similarity between two items. 
        Args:
            item1: item name 
            item2: other item name 
        Returns:
            similarity: value between 0 and 1
    """
   # Convert the texts into TF-IDF vectors
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([item1, item2])
    # Calculate the cosine similarity between the vectors
    similarity = cosine_similarity(vectors)
    return similarity[0, 1]

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
        sim = _compute_similarity_two_items(
            all_items['ITEM_NAME'][idx1], item_name)
        #add only 
        if sim > 0 and all_items['ITEM_ID'][idx1] != item_id: 
            data_row = [item_id, all_items['ITEM_ID'][idx1], sim]
            df_all_items_similarity_scores.loc[df_all_items_similarity_scores.size] = data_row
        

    return df_all_items_similarity_scores


def rank_data(df):
    """ Return the rank for each item per user. 
        Args:
            df: all user items            
        Returns:
            df_ranked: ranked user items based on number of transactions  
    """
    df['rank'] = df.groupby("user_id")["num_items"].rank(
       "dense", ascending=True)
    df_ranked = df[['user_id', 'ITEM_ID', 'comp_id', 'num_items', 'rank']]
    return df_ranked

def get_item_sim_scores(cnx, item_id):
    """Return all item SIM scores from a db. 
            cnx: database connection.
        Returns:
            df: a dataframe contains all transaction and for each:
            ITEM1_ID: Item ID
            ITEM2_ID: Item ID
            SIM: sim score  
        """
   
    # preparing a cursor object
    cursorObject = cnx.cursor(prepared=True)
    #select for an item 
    query =  'SELECT * from dcmdb.ITEM_SIM where ITEM1_ID = ' +  str(item_id)
    sim_scores = pd.read_sql(sql=query, con=cnx)       

    return sim_scores


def callculate_user_recommendations_online_content_based(count):
    """Find user item recommendations based on item names similirities.  
    Args:
        count: max number of recommnded items
    Returns: None
    """

    try:
      #delete current recomndations
      reset_recomndation_table()
      #wait for 5 seconds
      time.sleep(5)  # Sleep for 3 seconds

      cnx = mysql.connector.connect(**config)
      # connect to DB and get all transactions

      df_all_transactions = get_all_transactions_db(cnx)

      #rank user items
      df_ranked = rank_data(df_all_transactions)

      # get all items
      df_all_items = get_all_items(cnx=cnx)

      # read SIM scores
      df_all_items = get_item_sim_scores(cnx=cnx)
      cnx.close()

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
                df_item_similarity_scores = get_item_sim_scores(cnx=cnx, item_id=item_id)

                if len(df_item_similarity_scores == 0):
                    df_item_similarity_scores = compute_similarity_items(df_all_items, item_id, item_name) 
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
                            str(df_user_item_top_scores['SCORE'][idx] * 100)])

        # add user recommedned items
        print(attrRows)
        print()
        insert_user_recommendations_db(attrRows)
        time.sleep(3)  # Sleep for 3 seconds

    except mysql.connector.Error as err:
      if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
      elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
      else:
        print(err)


callculate_user_recommendations_online_content_based(10)

# cnx = mysql.connector.connect(**config)
# sim_scores = get_item_sim_scores(cnx=cnx, item_id=1)
# print(sim_scores)
