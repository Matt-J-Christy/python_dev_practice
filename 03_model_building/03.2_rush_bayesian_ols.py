#!/usr/bin/env python
# coding: utf-8

# # Modeling with Bayesian Regression
# 
# Going the Bayesian Route - https://docs.pymc.io/notebooks/GLM-linear.html

# In[1]:


# %load ../api_access_snippet.py
#import library
import gspread 
#Service client credential from oauth2client
from oauth2client.service_account import ServiceAccountCredentials
# Print nicely
import pprint
#Create scope
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
#create some credential using that scope and content of startup_funding.json
creds = ServiceAccountCredentials.from_json_keyfile_name('../quickstart/g_sheet_creds.json',scope)
#create gspread authorize using that credential
client = gspread.authorize(creds)
my_email = 'matthewjchristy66@gmail.com'

def read_file(sheet_name):
    out = client.open(sheet_name).sheet1
    out = out.get_all_values()
    out = pd.DataFrame(out, columns = out.pop(0))
    return(out)

import pandas as pd 
import numpy as np


# In[2]:


rush = read_file('rushing_data_model_ready')


# ## Quick Data Cleaning 

# In[3]:


target = ['rush_fantasy_pts']
last_week = ['last_week_Yds', 'last_week_TD', 'last_week_rush_fantasy_pts']
inputs = ['yds_ratio', 'fantasy_pts_ratio', 'lag2_Yds', 'lag2_rush_fantasy_pts', 'lag2_TD']
rush = rush.replace('na', np.NaN);
fix_vars = target + last_week + inputs + ['Week']
rush[fix_vars] = rush[fix_vars].astype(float)
rush.loc[rush.rush_fantasy_pts < 0, 'rush_fantasy_pts'] = 0
rush['log1p_target'] = np.log1p(rush.rush_fantasy_pts + 1)
rush['yds_ratio'] = rush['yds_ratio'].fillna(0)
rush['fantasy_pts_ratio'] = rush['fantasy_pts_ratio'].fillna(0)
rush['yds_ratio'] = rush['yds_ratio'].replace([np.inf, -np.inf], 0)
rush['fantasy_pts_ratio'] = rush['fantasy_pts_ratio'].replace([np.inf, -np.inf], 0)


# In[4]:


import matplotlib.pyplot as plt
plt.hist(np.log1p(rush.last_week_rush_fantasy_pts));


# In[5]:


plt.hist(rush.yds_ratio);


# In[6]:


plt.hist(rush.last_week_Yds);


# In[7]:


rush.Week.describe()


# ## Loading pymc3 and other packages

# In[8]:


import pymc3 as pm
#declaring model formulation
model_vars = ['log1p_target', 'last_week_rush_fantasy_pts', 'last_week_TD', 'last_week_Yds', 'yds_ratio', 'fantasy_pts_ratio', 'lag2_Yds', 'lag2_TD', 'lag2_rush_fantasy_pts']
f = 'log1p_target ~ np.log1p(last_week_rush_fantasy_pts) + last_week_TD + last_week_Yds + yds_ratio + fantasy_pts_ratio + lag2_Yds + lag2_TD + lag2_rush_fantasy_pts'
input_data = rush[model_vars].loc[rush['Week'] < 7, :]
score_data = rush[model_vars].loc[rush['Week'] == 7, :]


# ### Standard OLS

# In[ ]:


with pm.Model() as model:
    # specify glm and pass in data. The resulting linear model, its likelihood and
    # and all its parameters are automatically added to our model.
    pm.glm.GLM.from_formula(f, input_data, family=pm.glm.families.StudentT())
    trace = pm.sample(draws = 700, cores=4, init='adapt_diag', tune = 500) 
    # draw 700 posterior samples using NUTS sampling


# In[1]:


with pm.Model() as model:
    # specify glm and pass in data. The resulting linear model, its likelihood and
    # and all its parameters are automatically added to our model.
    obs_data = pm.Data('obs_data', input_data)
    pm.glm.GLM.from_formula(f, data = obs_data, family=pm.glm.families.StudentT())
    trace = pm.sample(draws = 700, cores=4, init='adapt_diag', tune = 500) 
    # draw 700 posterior samples using NUTS sampling


# In[15]:


#pm.save_trace(trace)


# In[ ]:


#trace = pm.load_trace('.pymc_2.trace')
#with pm.Model() as model:
    # specify glm and pass in data. The resulting linear model, its likelihood and
    # and all its parameters are automatically added to our model.
#    pm.glm.GLM.from_formula(f, input_data)


# In[25]:


ppc = pm.sample_ppc(trace, model=model, samples=500)


# In[35]:


#score_data_as_dict = score_data.to_dict(orient = 'list')
score_y = score_data.log1p_target
input_x = score_data.drop('log1p_target')
bleh = {'x': input_x, 'y': score_y}
with model:
    pm.set_data({'obs_data': score_data})
    y_preds = pm.sample_posterior_predictive(trace, keep_size = True)


# In[40]:


with model:
    pm.set_data(score_data.to_dict(orient = 'list'))
    y_preds = pm.sample_ppc(trace, samples=500)


# In[41]:


score_data.iloc[1:3, :].to_dict(orient = 'list')


# In[ ]:





# In[16]:


print(np.asarray(ppc['y']).shape)
print(rush.shape)


# In[17]:


np.mean(np.exp(np.asarray(ppc['y'])), axis = 0)


# In[20]:


fits = np.mean(np.exp(np.asarray(ppc['y'])), axis = 0)
fit_df = pd.DataFrame(data = fits, columns = ['fitted_value'])


# In[23]:


plt.hist(fit_df.fitted_value);


# In[18]:


rush.columns


# In[22]:


plt.subplots()
plt.scatter(rush.Week, rush.rush_fantasy_pts, label = 'obs rush pts', marker = 'o')
plt.scatter(rush.Week, y_pred, label = 'fitted values', marker = 'x')
plt.xlabel('NFL Week Num')
plt.ylabel('Rushing Fantasy Pts')


# In[26]:


plt.subplots()
plt.scatter(rush.Week, rush.rush_fantasy_pts.mean(), label = 'obs rush pts', marker = 'o')
plt.scatter(rush.Week, y_pred, label = 'fitted values', marker = 'x')
plt.xlabel('NFL Week Num')
plt.ylabel('Rushing Fantasy Pts')


# In[32]:


plt.errorbar(x=rush.log1p_target, y=y_pred, yerr=pred_sd, linestyle='', marker='o')
plt.plot(rush.log1p_target, y_pred, 'o')
plt.ylim(-.05, 1.05)
plt.xlabel('predictor')
plt.ylabel('outcome')


# ### Robust OLS 

# In[ ]:


with pm.Model() as model_robust:
    pm.glm.GLM.from_formula(f, rush, family=pm.glm.families.StudentT())
    trace_robust = pm.sample(draws = 700, cores=4, init='adapt_diag')


# In[12]:


rush.head()


# ## Model Evaluation Tools 

# In[ ]:


#creating function to loop through model building 
def build_model(formula, nfl_target_week, data, samples):
    input_data = data.loc[df['Week'] < nfl_target_week, :]
    score_data = data.loc[df['Week'] == nfl_target_week, :]
    y_obs = data.rush_fantasy_pts
    
    with pm.Model() as model:
        # specify glm and pass in data. The resulting linear model, its likelihood and
        # and all its parameters are automatically added to our model.
        pm.glm.GLM.from_formula(formula, input_data)
        trace = pm.sample(draws = samples, cores=4, init='adapt_diag') 
        
    #getting fitted values 
    ppc = pm.sample_posterior_predictive(score_data, model=model, samples=500)
    fit_array = np.mean(np.exp(np.asarray(ppc['y'])), axis = 0)
    fits = pd.DataFrame(fit_array, columns = ['fitted_value'])
    
    #getting fit delta and calculating difference 
    delta = y_obs - fits 
    rmse = np.sqrt(delta**2)
    
    #output list 
    model_info = (trace, rmse)


# In[25]:





# In[ ]:





# In[ ]:




