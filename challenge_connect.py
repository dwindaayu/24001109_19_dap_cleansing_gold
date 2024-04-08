import sqlite3

query = """

CREATE TABLE texts (text varchar(50000), text_processing varchar(50000));

"""


conn = sqlite3.connect("challenge_gold.db")
print("Opened database succesfully")

conn.execute(query)
# conn.commit()
conn.close()
print("Closed database")