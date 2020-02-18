#creating a moving avg function 
def move_avg(df, smooth_col, group_vals, window):
    l_mean = lambda x: x.rolling(window, 1).mean()
    out = df.groupby(group_vals)[smooth_col].transform(l_mean)
    return(out)