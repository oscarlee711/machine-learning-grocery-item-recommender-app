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

        # Insert USER_ORDER FROM STAGING_ORDER_TRANSACTION
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
        print("Inserted records into USER_ORDER FROM STAGING_ORDER_TRANSACTION")

        # Update Store ID in USER_ORDER table
        # Since the transaction data source does not has store, evenly assign stores to USER_ORDER records
        cursor.execute("UPDATE USER_ORDER SET STORE_ID = 110 WHERE RIGHT(USER_ID, 1) = '0'")
        conn.commit()

        cursor.execute("UPDATE USER_ORDER SET STORE_ID = 111 WHERE RIGHT(USER_ID, 1) = '1'")
        conn.commit()

        cursor.execute("UPDATE USER_ORDER SET STORE_ID = 112 WHERE RIGHT(USER_ID, 1) = '2'")
        conn.commit()

        cursor.execute("UPDATE USER_ORDER SET STORE_ID = 113 WHERE RIGHT(USER_ID, 1) = '3'")
        conn.commit()

        cursor.execute("UPDATE USER_ORDER SET STORE_ID = 114 WHERE RIGHT(USER_ID, 1) = '4'")
        conn.commit()

        cursor.execute("UPDATE USER_ORDER SET STORE_ID = 115 WHERE RIGHT(USER_ID, 1) = '5'")
        conn.commit()

        cursor.execute("UPDATE USER_ORDER SET STORE_ID = 116 WHERE RIGHT(USER_ID, 1) = '6'")
        conn.commit()

        cursor.execute("UPDATE USER_ORDER SET STORE_ID = 117 WHERE RIGHT(USER_ID, 1) = '7'")
        conn.commit()

        cursor.execute("UPDATE USER_ORDER SET STORE_ID = 118 WHERE RIGHT(USER_ID, 1) = '8'")
        conn.commit()

        cursor.execute("UPDATE USER_ORDER SET STORE_ID = 119 WHERE RIGHT(USER_ID, 1) = '9'")
        conn.commit()

        print("Updated STORE_ID in USER_ORDER records")

        conn.close()
        print("Database connection is closed")

except Error as e:
    print("Error while connecting to MySQL", e)

