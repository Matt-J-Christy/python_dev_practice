drop table if exists receiving_model_data;

create table receiving_model_data as

with base as (
select rec.Name, 
    rec.Team,
    cast(rec.Week as real) as Week,
    rec.Opp,
    rec.Score,
    rec.rec_fantasy_pts,
    rec.Yds,
    rec.TD,
    rec.Rec as receptions,
    past.yds_game as yds_2018,
    past.ppg as ppg_2018,
    past.td_per_game
from receiving_processed_step1 rec 
join receiving_2018 past 
    on past.Player = rec.Name
    ),
    
lag_step1 as (    
select *,

    lag(rec_fantasy_pts, 1, 0) over( partition by Name order by week desc) as lag1_fantasy_pts,
    lag(rec_fantasy_pts, 2, 0) over (partition by Name order by week desc) as lag2_fantasy_pts,
    avg(rec_fantasy_pts) over (partition by Name order by week desc 
        rows between 3 preceding and 1 preceding ) as avg_pts_3weeks,
    
    lag(Yds, 1, 0) over( partition by Name order by week desc) as lag1_yds,
    lag(Yds, 2, 0) over (partition by Name order by week desc) as lag2_yds,
    avg(Yds) over (partition by Name order by week desc 
        rows between 3 preceding and 1 preceding) as avg_yds_3weeks,
    
    lag(TD, 1, 0) over( partition by Name order by week desc) as lag1_tds,
    lag(TD, 2, 0) over (partition by Name order by week desc) as lag2_tds,
    avg(TD) over (partition by Name order by week desc 
        rows between 3 preceding and 1 preceding) as avg_tds_3weeks
from base
),

lag_step2 as (
    select Name,
        Week,
        Team,
        Opp,
        Score,
        rec_fantasy_pts,
        
        case when lag1_fantasy_pts = 0 or lag1_fantasy_pts is null then ppg_2018 else lag1_fantasy_pts end as lag1_fantasy_pts,
        case when lag2_fantasy_pts = 0 or lag2_fantasy_pts is null then ppg_2018 else lag2_fantasy_pts end as lag2_fantasy_pts,
        coalesce(avg_pts_3weeks, ppg_2018) as avg_pts_3weeks,
        
        case when lag1_yds = 0 or lag1_yds is null then yds_2018 else lag1_yds end as lag1_yds,
        case when lag2_yds = 0 or lag2_yds is null then yds_2018 else lag2_yds end as lag2_yds,
        coalesce(avg_yds_3weeks, yds_2018) as avg_yds_3weeks,
        
        case when lag1_tds = 0 or lag1_tds is null then td_per_game else lag1_tds end as lag1_tds,
        case when lag2_tds = 0 or lag2_tds is null then td_per_game else lag2_tds end as lag2_tds,
        coalesce(avg_tds_3weeks, td_per_game) as avg_tds_3weeks
    from lag_step1
)

select *,
    coalesce(lag1_fantasy_pts/avg_pts_3weeks, 0) as pts_ratio,
    coalesce(lag1_yds/avg_yds_3weeks, 0) as yds_ratio,
    coalesce(lag1_tds/avg_tds_3weeks, 0) as td_ratio
from lag_step2
