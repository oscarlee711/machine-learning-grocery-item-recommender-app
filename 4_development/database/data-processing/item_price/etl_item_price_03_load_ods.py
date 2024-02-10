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

        # WEEKLY INSERT AND UPDATE ODS_COLES_ITEM_PRICE from STAGING_COLES_ITEM_PRICE
        # Deduplicate imported Coles price data
        cursor.execute("DROP TABLE IF EXISTS STAGING_COLES_ITEM_PRICE_DEDUPLICATE")
        conn.commit()
        cursor.execute("""CREATE TABLE STAGING_COLES_ITEM_PRICE_DEDUPLICATE
                            SELECT 
                            COLES_PRICE_DATE, 
                            COLES_ITEM_NAME, 
                            MIN(COLES_ITEM_PRICE) AS COLES_ITEM_PRICE, 
                            MIN(COLES_ITEM_UNIT_PRICE) AS COLES_ITEM_UNIT_PRICE 
                            FROM STAGING_COLES_ITEM_PRICE 
                            WHERE WOOLY_ITEM_PRICE <> 'NULL' 
                            GROUP BY COLES_PRICE_DATE, COLES_ITEM_NAME""")
        conn.commit()
        print("Deduplicate imported Coles price data in table STAGING_COLES_ITEM_PRICE_DEDUPLICATE")

        # Delete insert imported Coles price data into ODS_COLES_ITEM_PRICE
        cursor.execute("TRUNCATE TABLE ODS_COLES_ITEM_PRICE")
        conn.commit()
        cursor.execute("""INSERT INTO ODS_COLES_ITEM_PRICE
                            SELECT
                            COLES_PRICE_DATE,
                            B.ITEM_ID,
                            COLES_ITEM_NAME,
                            SUBSTRING(COLES_ITEM_PRICE,2,10),
                            COLES_ITEM_UNIT_PRICE
                            FROM STAGING_COLES_ITEM_PRICE_DEDUPLICATE A
                            INNER JOIN ITEM B 
                            ON UPPER(A.COLES_ITEM_NAME) = UPPER(B.ITEM_NAME)""")
        conn.commit()
        print("Delete insert imported Coles price data into ODS_COLES_ITEM_PRICE")

        # WEEKLY INSERT AND UPDATE ODS_WOOLY_ITEM_PRICE from STAGING_WOOLY_ITEM_PRICE
        # Deduplicate imported Wooly price data
        cursor.execute("DROP TABLE IF EXISTS STAGING_WOOLY_ITEM_PRICE_DEDUPLICATE")
        conn.commit()
        cursor.execute("""CREATE TABLE STAGING_WOOLY_ITEM_PRICE_DEDUPLICATE
                            SELECT 
                            WOOLY_PRICE_DATE, 
                            WOOLY_ITEM_NAME, 
                            MIN(WOOLY_ITEM_PRICE) AS WOOLY_ITEM_PRICE, 
                            MIN(WOOLY_ITEM_UNIT_PRICE) AS WOOLY_ITEM_UNIT_PRICE 
                            FROM STAGING_WOOLY_ITEM_PRICE 
                            WHERE WOOLY_ITEM_PRICE <> 'NULL' 
                            GROUP BY WOOLY_PRICE_DATE, WOOLY_ITEM_NAME""")
        conn.commit()
        print("Deduplicate imported Wooly price data in table STAGING_WOOLY_ITEM_PRICE_DEDUPLICATE")

        # Delete insert imported Wooly price data into ODS_WOOLY_ITEM_PRICE
        cursor.execute("TRUNCATE TABLE ODS_WOOLY_ITEM_PRICE")
        conn.commit()
        cursor.execute("""INSERT INTO ODS_WOOLY_ITEM_PRICE
                            SELECT
                            WOOLY_PRICE_DATE,
                            B.ITEM_ID,
                            WOOLY_ITEM_NAME,
                            SUBSTRING(WOOLY_ITEM_PRICE,2,10),
                            WOOLY_ITEM_UNIT_PRICE
                            FROM STAGING_WOOLY_ITEM_PRICE_DEDUPLICATE A
                            INNER JOIN ITEM B 
                            ON UPPER(A.WOOLY_ITEM_NAME) = UPPER(B.ITEM_NAME)""")
        conn.commit()
        print("Delete insert imported Wooly price data into ODS_WOOLY_ITEM_PRICE")

        conn.close()
        print("Database connection is closed")

except Error as e:
    print("Error while connecting to MySQL", e)

