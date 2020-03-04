def get_url(url):
    #grabbing the HTML and getting text 
    my_header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'}
    fantasy_page = get(url, headers = my_header)
    
    return(fantasy_page)
    
def get_headers(html):
    
    doc = lh.fromstring(html.content)
    
    #getting column names 
    title = doc.xpath('//tr//th')
    
    colnames = []

    n = len(title)

    for i in range(0, n):
        name = title[i].text_content()
        colnames.append(name)
    
    return(colnames)    
    
    
def get_table_data(html, colnames):
     
    #parsing table elements in the HTML inside the pattern "//tr" --> this is a table element 
    doc = lh.fromstring(html.content)
    table_elements = doc.xpath('//tr')
    
    #creating an empty array to insert the table elements 
    cols = []

    for j in range(0, len(colnames)):
        name = colnames[j] #getting the column name from the HTML table 
        #print('%d:"%s"'% (i, name))
        cols.append((name, []))

   #Since out first row is the header, data is stored on the second row onwards

    for j in range(1,len(table_elements)):
        #T is our j'th row
        T=table_elements[j]

        #If row is not of size 24, the //tr data is not from our table 
        if len(T)!=len(colnames):
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
    return(cols)
    
def create_df(cols):
    #creating a dictionary for the columns in the parsed table 
    Dict={title:column for (title,column) in cols}

    df=pd.DataFrame(Dict)
    return(df)
    
def clean_df(df, page_url):
    #data cleaning 
    escapes = ''.join([chr(char) for char in range(1, 32)])
    translator = str.maketrans('', '', escapes)
    df.columns = df.columns.str.translate(translator)
    
    #fixing escape charaters
    fixed = ['Name', 'Team', 'Opp', 'Score']
    for i in fixed:
        df.loc[:, i] = df.loc[:, i].astype(str).str.translate(translator)
    import re 
    week = re.search('week=(.*)&season', urls[0]).group(1)
     
    df.insert(1, 'Week', week)
    
    #casting to strings 
    df = df.astype(str)
       
    #returning the df
    return(df)