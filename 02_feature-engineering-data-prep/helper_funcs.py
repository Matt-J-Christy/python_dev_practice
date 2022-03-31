# helper functions for feature engineering
import gspread
import os
from oauth2client.service_account import ServiceAccountCredentials

# what my default credential look like

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
# create some credential using that scope and content of startup_funding.json

creds_file = os.path.join(
    os.path.dirname(__file__),
    '../g_sheet_creds.json'
)

creds = ServiceAccountCredentials.from_json_keyfile_name(
    creds_file, scope)
# create gspread authorize using that credential
client = gspread.authorize(creds)
my_email = 'matthewjchristy66@gmail.com'


def passing_pts(df):
    # declaring the scoring parameters for passing stats
    pts = {
        "yds": .04,
        "td": 4,
        "300yd": 3,
        "int": -1,
        "fumble": -1
    }
    # applyting to the data
    score = df["Yds"]*pts['yds'] + df['TD'] * pts['td'] + df['Int'] * \
        pts['int'] + df['FUM'] * pts['fumble'] + df['300yd_flag']*pts['300yd']

    return(score)


def receiving_rush_pts(df):
    pts = {
        "yds": .1,
        "td": 6,
        "100yds": 3,
        "fumble": -1,
        "2pt": 2
    }

    score = df["Yds"]*pts['yds'] + df['TD'] * pts['td']
    + df['FUM'] * pts['fumble'] + df['100yd_flag']*pts['100yds']

    return(score)

# creating a moving avg function


def move_avg(df, smooth_col, group_vals, window):
    def l_mean(x): return x.rolling(window, 1).mean()
    out = df.groupby(group_vals)[smooth_col].transform(l_mean)
    return(out)


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
    except gspread.exceptions.SpreadsheetNotFound:
        # creating sheets
        # Now will can access our google sheets we call
        #  client.open on StartupName
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

    print(f"{sheet_name} successfully written")
