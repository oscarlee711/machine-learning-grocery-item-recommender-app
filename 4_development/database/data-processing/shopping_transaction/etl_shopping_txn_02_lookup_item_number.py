import pandas as pd
import mysql.connector as msql
from mysql.connector import Error

df = pd.read_csv('//Users//oscar//Documents//LOOKUP_ORDER_TRANSACTION_ITEM_ID_SQL.csv', index_col=False, delimiter='\t')
print(df)

try:
    conn = msql.connect(host='34.129.54.95', user='dcmdbuser',
                        password='dusit2022t3')#give ur username, password
    if conn.is_connected():
        cursor = conn.cursor()
        print("Database is connected")
        cursor.execute("use dcmdb")
        print("Connected to dcmdb")
        cursor.execute("TRUNCATE TABLE LOOKUP_ORDER_TRANSACTION_ITEM_ID")
        conn.commit()
        print("Delete all records in LOOKUP_ORDER_TRANSACTION_ITEM_ID table")

        for row in df.itertuples():
            sql = str(row[1])
            cursor.execute(sql)
            result = cursor.fetchone()
            if result is not None:
                print(result[1])
                ITEM_DESC = str(result[0])
                LOOKUP_ITEM_NAME = str(result[1])
                LOOKUP_ITEM_NAME = LOOKUP_ITEM_NAME.replace("'", "")
                LOOKUP_ITEM_ID = str(result[2])
                insertSQL = "INSERT INTO LOOKUP_ORDER_TRANSACTION_ITEM_ID VALUES ('" + ITEM_DESC + "','" + LOOKUP_ITEM_NAME + "','" + LOOKUP_ITEM_ID + "');"
                print(insertSQL)
                cursor.execute(insertSQL)
                conn.commit()
                print("Insert item: " + ITEM_DESC)

        conn.close()
        print("Database connection is closed")
except Error as e:
    print("Error while connecting to MySQL", e)
