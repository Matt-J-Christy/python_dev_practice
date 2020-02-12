def exp_smooth(df, smooth_col, alpha, lag):
     series = lambda x: x.rolling(lag, 1)  