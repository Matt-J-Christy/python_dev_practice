# NFL Fantasy Model & Application 

## Project Outline 
1. web scrape the data or use API the write to Google drive
2. write data to SQLite DB and feature engineer
3. model for player score 
    - create 3 different models for passing, rushing and receiving yards
    - add scores and calculate estimated total score
    - candidate models:
        - OLS (regular linear regression)
        - mixed Effects model
        - some combination of GLM for E[score > 0] and OLS for E[score | score > 0]
4. develop dashboard for vizsualizations and player recommendations
5. build optimazation process for line-up generation 

## Project Status 
1. Code is in an O.K. place, but the current scraping process is rusted. (Thanks NLF dot com for changing your website)
    - looking for API to get more reliable data source and more features
2. Feature engineering using SQLite is done 
    - player panel data ready for modeling. 
    - in the future looking to add data on opp defensive rank, active status and depth chart status 
3. WIP
4. Not Started 
5. Not Started

    
