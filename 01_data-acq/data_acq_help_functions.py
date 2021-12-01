# helper functions

# importing various libraries

import gspread
from requests import get
import lxml.html as lh
from bs4 import BeautifulSoup
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd


# what my default credential look like 

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
#create some credential using that scope and content of startup_funding.json
creds = ServiceAccountCredentials.from_json_keyfile_name('../quickstart/g_sheet_creds.json',scope)
#create gspread authorize using that credential
client = gspread.authorize(creds)
my_email = 'matthewjchristy66@gmail.com'



def get_url(url):
    # grabbing the HTML and getting text
    my_header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'}
    fantasy_page = get(url, headers=my_header)

    return(fantasy_page)


def get_headers(html):

    doc = lh.fromstring(html.content)

    # getting column names
    title = doc.xpath('//tr//th')

    colnames = []

    n = len(title)

    for i in range(0, n):
        name = title[i].text_content()
        colnames.append(name)

    return(colnames)


def get_table_data(html, colnames):

    # parsing table elements in the HTML inside the pattern "//tr" --> this is a table element
    doc = lh.fromstring(html.content)
    table_elements = doc.xpath('//tr')

    # creating an empty array to insert the table elements
    cols = []

    for j in range(0, len(colnames)):
        name = colnames[j]  # getting the column name from the HTML table
        #print('%d:"%s"'% (i, name))
        cols.append((name, []))

   # Since out first row is the header, data is stored on the second row onwards

    for j in range(1, len(table_elements)):
        # T is our j'th row
        T = table_elements[j]

        # If row is not of size 24, the //tr data is not from our table
        if len(T) != len(colnames):
            break

        # i is the index of our column
        i = 0

        # Iterate through each element of the row
        for t in T.iterchildren():
            data = t.text_content()

            # Append the data to the empty list of the i'th column
            cols[i][1].append(data)
            # Increment i for the next column
            i += 1
    return(cols)


def create_df(cols):
    # creating a dictionary for the columns in the parsed table
    Dict = {title: column for (title, column) in cols}

    df = pd.DataFrame(Dict)
    return(df)


def clean_df(df, page_url):
    # data cleaning
    escapes = ''.join([chr(char) for char in range(1, 32)])
    translator = str.maketrans('', '', escapes)
    df.columns = df.columns.str.translate(translator)

    # fixing escape charaters
    fixed = ['Name', 'Team', 'Opp', 'Score']
    for i in fixed:
        df.loc[:, i] = df.loc[:, i].astype(str).str.translate(translator)
    import re
    week = re.search('week=(.*)&season', page_url[0]).group(1)

    df.insert(1, 'Week', week)

    # casting to strings
    df = df.astype(str)

    # returning the df
    return(df)


def writer(data, sheet_name, share_email):
    """
    function to write cleaned data to a google sheet 
    and share it with my email
    """

    # Grabbing Parameters for looping
    n_rows = data.shape[0]
    n_cols = data.shape[1]

    # load sheet if it exists or create and share sheet if it does not
    try:
        sheet = client.open(sheet_name)
    except:
        # creating sheets
          # Now will can access our google sheets we call client.open on StartupName
        sheet = client.create(sheet_name)
        sheet.share(share_email,  perm_type='user',
                    role='writer')  # sharing my email

    # getting cell list to batch update
    import string
    end_col = string.ascii_uppercase[n_cols - 1]
    end_row = n_rows + 1

    sheet_range = 'A1:' + end_col + str(end_row)

    # turning df to one long list
    df_as_list = data.stack().tolist()
    df_as_list = data.columns.tolist() + df_as_list

    # getting the target sheet
    ws = sheet.get_worksheet(0)
    cell_list = ws.range(sheet_range)

    # writing df list to cell range list
    for i in range(0, len(cell_list)):
        cell_list[i].value = df_as_list[i]

    # batch updating
    ws.update_cells(cell_list)
