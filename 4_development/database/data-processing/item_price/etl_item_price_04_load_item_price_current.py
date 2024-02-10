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

        # WEEKLY INSERT AND UPDATE ITEM_PRICE_CURRENT from ODS_WOOLY_ITEM_PRICE
        cursor.execute("TRUNCATE TABLE ITEM_PRICE_CURRENT")
        conn.commit()
        cursor.execute("""INSERT INTO ITEM_PRICE_CURRENT
                            SELECT 
                            DISTINCT 
                            ITEM_ID,
                            1,
                            WOOLY_ITEM_PRICE,
                            0,	
                            0,
                            WOOLY_ITEM_PRICE,
                            WOOLY_ITEM_PRICE
                            FROM ODS_WOOLY_ITEM_PRICE""")
        conn.commit()
        print("Delete insert latest weekly Woolworths data into ITEM_PRICE_CURRENT")

        # WEEKLY INSERT AND UPDATE ITEM_PRICE_CURRENT from Coles datafile
        cursor.execute("""INSERT INTO ITEM_PRICE_CURRENT
                            SELECT 
                            DISTINCT 
                            ITEM_ID,
                            2,
                            COLES_ITEM_PRICE,
                            0,
                            0,
                            COLES_ITEM_PRICE,
                            COLES_ITEM_PRICE
                            FROM ODS_COLES_ITEM_PRICE""")
        conn.commit()
        print("Delete insert latest weekly Coles data into ITEM_PRICE_CURRENT")

        # Calculate the maximum and minimum price of items from ITEM_PRICE_HIST
        cursor.execute("TRUNCATE TABLE ITEM_PRICE_MIN_MAX")
        conn.commit()

        cursor.execute("""INSERT INTO ITEM_PRICE_MIN_MAX 
                            SELECT 
                            ITEM_ID, 
                            MAX(IPH_ITEM_BASE_PRICE) AS MAX_PRICE, 
                            MIN(IPH_ITEM_BASE_PRICE) AS MIN_PRICE
                            FROM ITEM_PRICE_HIST 
                            GROUP BY ITEM_ID""")
        conn.commit()

        # Update highest and lowest price from ITEM_PRICE_HIST
        cursor.execute("""UPDATE ITEM_PRICE_CURRENT A
                            INNER JOIN ITEM_PRICE_MIN_MAX B ON A.ITEM_ID = B.ITEM_ID
                            SET 
                            A.IP_FOUR_WK_HIGHEST_PRICE = B.MAX_ITEM_PRICE,
                            A.IP_FOUR_WK_LOWEST_PRICE = B.MIN_ITEM_PRICE""")
        conn.commit()

        # Update discount price
        cursor.execute("""UPDATE ITEM_PRICE_CURRENT 
                            SET IP_ITEM_DISCOUNT_PRICE = IP_FOUR_WK_HIGHEST_PRICE -  IP_ITEM_BASE_PRICE""")
        conn.commit()

        # Update discount price percentage
        cursor.execute("""UPDATE ITEM_PRICE_CURRENT 
                            SET IP_ITEM_DISCOUNT_PCT = ROUND(IP_ITEM_DISCOUNT_PRICE / 
                            (IP_ITEM_BASE_PRICE + IP_ITEM_DISCOUNT_PRICE), 2)""")
        conn.commit()

        conn.close()
        print("Database connection is closed")

except Error as e:
    print("Error while connecting to MySQL", e)

