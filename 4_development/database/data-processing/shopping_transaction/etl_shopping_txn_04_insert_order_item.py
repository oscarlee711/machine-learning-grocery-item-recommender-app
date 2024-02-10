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

        # Insert ORDER_ITEM table FROM STAGING_ORDER_TRANSACTION
        cursor.execute("""INSERT INTO ORDER_ITEM
                            SELECT 
                            CONCAT(REPLACE(A.USER_ORDER_DATE,'-',''),A.USER_ID) AS ORDER_ID,
                            B.LOOKUP_ITEM_ID AS ITEM_ID,
                            COUNT(1) AS ORDER_ITEM_QTY,
                            C.IP_ITEM_BASE_PRICE AS ORDER_ITEM_BASE_PRICE,
                            C.IP_ITEM_DISCOUNT_PRICE AS ORDER_ITEM_DISCOUNT_PRICE
                            FROM STAGING_ORDER_TRANSACTION A 
                            LEFT JOIN LOOKUP_ORDER_TRANSACTION_ITEM_ID B
                            ON A.ITEM_DESC = B.ITEM_DESC
                            LEFT JOIN ITEM_PRICE_CURRENT C
                            ON B.LOOKUP_ITEM_ID = C.ITEM_ID
                            GROUP BY 
                            CONCAT(REPLACE(A.USER_ORDER_DATE,'-',''),A.USER_ID),
                            B.LOOKUP_ITEM_ID,
                            C.IP_ITEM_BASE_PRICE,
                            C.IP_ITEM_DISCOUNT_PRICE""")
        conn.commit()
        print("Inserted records into ORDER_ITEM FROM STAGING_ORDER_TRANSACTION")

        conn.close()
        print("Database connection is closed")

except Error as e:
    print("Error while connecting to MySQL", e)

