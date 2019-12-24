
def scraper(page_url, sheet_name, share_mail): 
    
    my_header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'}
    
    #grabbing the HTML and getting text 
    fantasy_page = get(page_url, headers = my_header)

    doc = lh.fromstring(fantasy_page.content)
    
    print(fantasy_page)
    
    #parsing table elements in the HTML inside the pattern "//tr" --> this is a table element 

    table_elements = doc.xpath('//tr')
    
    #getting column names 
    title = doc.xpath('//tr//th')
    
    colnames = []

    n = len(title)

    for i in range(0, n):
        name = title[i].text_content()
        colnames.append(name)
            
  #creating an empty array to insert the table elements 
    cols = []

    i = 0 #setting the increment 

    for j in range(0, len(colnames)):
        i+1
        name = colnames[j] #getting the column name from the HTML table 
        #print('%d:"%s"'% (i, name))
        cols.append((name, []))

   #Since out first row is the header, data is stored on the second row onwards

    for j in range(1,len(table_elements)):
        #T is our j'th row
        T=table_elements[j]

        #If row is not of size 24, the //tr data is not from our table 
        if len(T)!=12:
            break

        #i is the index of our column
        i=0

        #Iterate through each element of the row
        for t in T.iterchildren():
            data=t.text_content() 

            #Append the data to the empty list of the i'th column
            cols[i][1].append(data)
            #Increment i for the next column
            i+=1
        
    #creating a dictionary for the columns in the parsed table 
    Dict={title:column for (title,column) in cols}

    df=pd.DataFrame(Dict)
    
    #data cleaning 
    escapes = ''.join([chr(char) for char in range(1, 32)])
    translator = str.maketrans('', '', escapes)
    df.columns = df.columns.str.translate(translator)
    
    #fixing escape charaters
    fixed = ['Name', 'Team', 'Opp', 'Score']
    for i in fixed:
        df.loc[:, i] = df.loc[:, i].astype(str).str.translate(translator)
        
    #Grapping Parameters for looping 
    n_rows = df.shape[0]
    n_cols = df.shape[1]
    
    #writing to google sheets 
    import time 

    #Now will can access our google sheets we call client.open on StartupName
    sheet = client.create(sheet_name) #2019-q4_fantasy-web-scraping/passing

    sheet.share(share_mail,  perm_type='user', role='writer') #sharing my email 
    
    #writing data to the worksheet
    ws = sheet.get_worksheet(0)

    shaped_data = df.transpose()

    ws.insert_row(df.columns.tolist(), 1)

    for i in range(1, n_rows+1): 
        row = df.iloc[i-1].tolist()
        index = i+1
        if i%10 == 0: #printing the step in the loop
            print(i)  
            time.sleep(15)
            
        ws.insert_row(row, index) #writing the data 
    
    print('row ', i, ' end of file')
    time.sleep(45)