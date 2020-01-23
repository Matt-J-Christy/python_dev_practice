def writer(data, sheet_name, share_email):
    #Grabbing Parameters for looping 
    n_rows = data.shape[0]
    n_cols = data.shape[1]
    
    #creating sheets
     #Now will can access our google sheets we call client.open on StartupName
    sheet = client.create(sheet_name) 
    sheet.share(share_email,  perm_type='user', role='writer') #sharing my email 
    
    #getting cell list to batch update
    import string
    end_col = string.ascii_uppercase[n_cols - 1]
    end_row = n_rows + 1
    
    sheet_range = 'A1:'+ end_col + str(end_row)
    
    #turning df to one long list 
    df_as_list = data.stack().tolist()
    df_as_list = data.columns.tolist() + df_as_list
    
    #getting the target sheet 
    ws = sheet.get_worksheet(0)
    cell_list = ws.range(sheet_range)
    
    #writing df list to cell range list 
    for i in range(0, len(cell_list)):
        cell_list[i].value = df_as_list[i]
        
    #batch updating 
    ws.update_cells(cell_list)