def passing_pts(df):
    #declaring the scoring parameters for passing stats 
    pts = {
        "yds":.04,
        "td":4,
        "300yd":3, 
        "int":-1,
        "fumble":-1
            }
    #applyting to the data 
    score = df["Yds"]*pts['yds'] + df['TD'] * pts['td'] + df['Int'] * pts['int'] + df['FUM'] * pts['fumble'] + df['300yd_flag']*pts['300yd']
    
    return(score)
    
def receiving_rush_pts(df): 
    pts = {
        "yds":.1,
        "td":6,
        "100yds":3,
        "fumble":-1,
        "2pt": 2
    }

        score = df["Yds"]*pts['yds'] + df['TD'] * pts['td']
        + df['FUM'] * pts['fumble'] + df['100yd_flag']*pts['100yd']

        return(score)