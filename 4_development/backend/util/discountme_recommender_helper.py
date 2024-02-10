import mysql.connector
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

#DB config
config = {
    'user': 'mohamed',
    'password': 'p@ssword0503',
    'host': '34.129.54.95',
    'database': 'dcmdb',
    'raise_on_warnings': True
}

# connect to DB
cnx = mysql.connector.connect(**config)

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


def get_all_transactions_db():
    """Return all transactions from a db. 
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
    query += " group by uo.USER_ID, c.COM_ID, o.ITEM_ID, i.ITEM_NAME order by uo.USER_ID"

    #execute query 
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

#clear recommendation table
def reset_recommendation_table():
    """Delete current recommendations.
    Args: None
    Returns: None
    """   
    # preparing a cursor object
    cursorObject = cnx.cursor()
    # deleting data from the RECOMMEND_ITEM table
    query = "DELETE FROM RECOMMEND_ITEM_TEMP"
    cursorObject.execute(query) 
    # data deleted
    cnx.commit() 

def insert_user_recommendations_db(attrRows):
    """Update recomndation table.
    Args:
        df: dataframe contains recpmndation records
    Returns: None
    """
    # preparing a cursor object
    cursorObject = cnx.cursor(prepared=True)
    # inserting data into the RECOMMEND_ITEM table
    query = """INSERT INTO RECOMMEND_ITEM_TEMP
              VALUES (%s, %s, %s, %s)"""
    for attrValues in attrRows:
        try:
            cursorObject.execute(query, attrValues)
        except Exception as err:
            print(err)

    # data inserted
    cnx.commit() 
    
def insert_item_sims_db(attrRows):
    """Update item sim table.
    Args:
        df: dataframe contains item sim records
    Returns: None
    """
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

# get all items  
def get_all_items():
    """ Return all items from a db. 
        Returns:
            df: a dataframe contains all items
    """
    query = "SELECT i.ITEM_ID, i.ITEM_NAME from ITEM i"
    df_all_items = pd.read_sql(sql=query, con=cnx)
    return df_all_items 

def get_item_sim_scores(item_id = None):
    """Return all item SIM scores from a db. 
            cnx: database connection.
        Returns:
            df: a dataframe contains all transaction and for each:
            ITEM1_ID: Item ID
            ITEM2_ID: Item ID
            SIM: sim score  
        """  
   
    #select for an item 
    if item_id == None:
        query =  'SELECT * from dcmdb.ITEM_SIM'
    else:
        query =  'SELECT * from dcmdb.ITEM_SIM where ITEM1_ID = ' +  str(item_id)

    sim_scores = pd.read_sql(sql=query, con=cnx)       
    return sim_scores 

def compute_similarity_two_items(item1, item2):
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

#evaluate content-based model 
def evaluate_cbrs(test_set, recommendations):
    total_precision = 0
    total_recall = 0
    num_users = len(test_set)

    for user, items in test_set.items():
        relevant_items = set(items)  # Items rated positively by the user
        recommended_items = set(recommendations[user])  # Items recommended by the CBRS

        # Calculate precision
        precision = len(relevant_items.intersection(recommended_items)) / len(recommended_items)
        total_precision += precision

        # Calculate recall
        recall = len(relevant_items.intersection(recommended_items)) / len(recommended_items)
        total_recall += recall

    avg_precision = total_precision / num_users
    avg_recall = total_recall / num_users

    return avg_precision, avg_recall

