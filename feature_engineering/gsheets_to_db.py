"""
create a sqlite db
and insert fantasy data for
feature engineering
"""

# importing various libraries
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import sqlite3

# Create scope
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(
    'g_sheet_creds.json', scope)
# create gspread authorize using that credential
client = gspread.authorize(creds)
my_email = 'matthewjchristy66@gmail.com'


def read_file(sheet_name):
    out = client.open(sheet_name).sheet1
    out = out.get_all_values()
    out = pd.DataFrame(out, columns=out.pop(0))
    return(out)


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


# connecting to the db and writing data

# if __name__ == '__main__':
#     create_connection(r"C:\Users\chris\pythonsqlite.db")


db_name = 'pythonsqlite.db'

conn = sqlite3.connect(db_name)


files = ['passing_processed_step1',
         'rushing_processed_step1',
         'receiving_processed_step1',
         '2018_passing_recap',
         '2018_rushing_recap',
         '2018_receiving_recap']

for file in files:
    data = read_file(file)

    data.drop_duplicates().to_sql(
        name=file,
        con=conn,
        if_exists='replace',
        index=False
    )

    print(f"writing table {file}")
