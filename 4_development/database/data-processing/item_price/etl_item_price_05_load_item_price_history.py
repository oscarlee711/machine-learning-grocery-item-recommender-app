import mysql.connector as msql
from mysql.connector import Error

try:
    conn = msql.connect(host='34.129.54.95', user='dcmdbuser',
                        password='dusit2022t3')#give ur username, password
    if conn.is_connected():
        cursor = conn.cursor()
        print("Database is connected")
        cursor.execute("use dcmdb")
        print("Connected to dcmdb")

        # Weekly Insert ITEM_PRICE_HIST from ODS_WOOLY_ITEM_PRICE and ODS_COLES_ITEM_PRICE
        cursor.execute("""INSERT INTO ITEM_PRICE_HIST                                                        
                            SELECT 
                            ITEM_ID,
                            1,
                            WOOLY_PRICE_DATE,
                            WOOLY_ITEM_PRICE,
                            NULL,
                            NULL
                            FROM 
                            ODS_WOOLY_ITEM_PRICE 
                            UNION ALL 
                            SELECT 
                            ITEM_ID,
                            2,
                            COLES_PRICE_DATE,
                            COLES_ITEM_PRICE,
                            NULL,
                            NULL
                            FROM ODS_COLES_ITEM_PRICE""")
        conn.commit()

        cursor.execute("UPDATE ITEM_PRICE_HIST SET IPH_ITEM_DISCOUNT_PRICE = NULL, IPH_ITEM_DISCOUNT_PCT = NULL")
        conn.commit()

        cursor.execute("""UPDATE ITEM_PRICE_HIST A
                            INNER JOIN ITEM_PRICE_MIN_MAX B ON A.ITEM_ID = B.ITEM_ID
                            SET A.IPH_ITEM_DISCOUNT_PRICE = B.MAX_ITEM_PRICE -  A.IPH_ITEM_BASE_PRICE""")
        conn.commit()

        cursor.execute("""UPDATE ITEM_PRICE_HIST SET IPH_ITEM_DISCOUNT_PCT 
                            = ROUND(IPH_ITEM_DISCOUNT_PRICE / (IPH_ITEM_BASE_PRICE + IPH_ITEM_DISCOUNT_PRICE), 2)""")
        conn.commit()

        cursor.execute("UPDATE ITEM_PRICE_HIST SET IPH_ITEM_DISCOUNT_PRICE = 0 WHERE IPH_ITEM_DISCOUNT_PRICE IS NULL")
        conn.commit()

        cursor.execute("UPDATE ITEM_PRICE_HIST SET IPH_ITEM_DISCOUNT_PCT = 0 WHERE IPH_ITEM_DISCOUNT_PCT IS NULL")
        conn.commit()

        print("Inserted latest weekly price data into ITEM_PRICE_HIST")
        conn.close()
        print("Database connection is closed")

except Error as e:
    print("Error while connecting to MySQL", e)

