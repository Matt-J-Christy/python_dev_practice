drop table if exists temp.base;

create temporary table base (
    Name text,
    Week int,
    Team text,
    Opp text,
    Score text,
    Comp real,
    Att real,
    Yds real,
    TD real,
    `Int` real,
    Sck real,
    FUM real,
    Rate real,
    `300yd_flag` real,
    passing_fantasy_pts real,
    ypg_2018 real,
    ppg_2018 real,
    td_per_game real,
    int_per_game real,
    qbr_2018 real
);

insert into base
select pass.*,
    past.yds_game as ypg_2018,
    past.ppg as ppg_2018,
    past.td_per_game,
    past.int_per_game,
    past.Rate as qbr_2018
from passing_processed_step1 pass 
left join passing_2018 past on 
    past.Player = pass.Name;


/*
columns to lag & 3 week avg:
- Yds
- QBR (Rate)
- passing_fantasy_pts
*/

drop table if exists passing_model_data;

create table passing_model_data as 

with lag_step1 as (
select *,

    lag(passing_fantasy_pts, 1, 0) over( partition by Name order by Week desc) as lag1_fantasy_pts,
    lag(passing_fantasy_pts, 2, 0) over( partition by Name order by Week desc) as lag2_fantasy_pts,
    avg(passing_fantasy_pts) over( partition by Name order by Week desc
    rows between 3 preceding and 1 preceding ) as avg_pts_3weeks,
    
    lag(Rate, 1, 0) over( partition by Name order by Week desc) as lag1_rate,
    lag(Rate, 2, 0) over( partition by Name order by Week desc) as lag2_rate,
    avg(Rate) over( partition by Name order by Week desc
    rows between 3 preceding and 1 preceding ) as avg_qbr_3weeks,
    
    lag(Yds, 1, 0) over( partition by Name order by Week desc) as lag1_yds,
    lag(Yds, 2, 0) over( partition by Name order by Week desc) as lag2_yds,
    avg(Yds) over( partition by Name order by Week desc
    rows between 3 preceding and 1 preceding ) as avg_yds_3weeks
from base
),

lag_step2 as (
select Name,
    Week,
    Team, 
    Opp,
    Rate,
    passing_fantasy_pts,
    
    case when lag1_fantasy_pts = 0 or lag1_fantasy_pts is null then ppg_2018 else lag1_fantasy_pts end as lag1_fantasy_pts,
    case when lag2_fantasy_pts = 0 or lag2_fantasy_pts is null then ppg_2018 else lag2_fantasy_pts end as lag2_fantasy_pts,
    coalesce(avg_pts_3weeks, ppg_2018) as avg_pts_3weeks,
    
    case when lag1_rate = 0 or lag1_rate is null then qbr_2018 else lag1_rate end as lag1_qbr,
    case when lag2_rate = 0 or lag2_rate is null then qbr_2018 else lag2_rate end as lag2_qbr,
    coalesce(avg_qbr_3weeks, qbr_2018) as avg_qbr_3weeks,
    
    case when lag1_yds = 0 or lag1_yds is null then ypg_2018 else lag1_yds end as lag1_yds,
    case when lag2_yds = 0 or lag2_yds is null then ypg_2018 else lag2_yds end as lag2_yds,
    coalesce(avg_yds_3weeks, ypg_2018) as avg_yds_3weeks
    
from lag_step1
)

select *,
    coalesce(lag1_fantasy_pts/avg_pts_3weeks, 0) as pts_ratio,
    coalesce(lag1_qbr/avg_qbr_3weeks, 0) as qbr_ratio,
    coalesce(lag1_yds/avg_yds_3weeks, 0) as yds_ratio
from lag_step2
