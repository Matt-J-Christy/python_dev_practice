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
    past.Player = pass.Name
where Name = 'Tom Brady';


/*

columns to lag & 3 week avg:
- Yds
- QBR (Rate)
- passing_fantasy_pts

*/

select *,

    lag(passing_fantasy_pts, 1, 0) over( partition by Name order by Week desc) as lag1_fantasy_pts,
    lag(passing_fantasy_pts, 2, 0) over( partition by Name order by Week desc) as lag2_fantasy_pts,
    avg(passing_fantasy_pts) over( partition by Name order by Week desc
    rows between 3 preceding and 1 preceding ) as avg_pts_3weeks,
    
    lag(Rate, 1, 0) over( partition by Name order by Week desc) as lag1_rate_pts,
    lag(Rate, 2, 0) over( partition by Name order by Week desc) as lag2_rate_pts,
    avg(Rate) over( partition by Name order by Week desc
    rows between 3 preceding and 1 preceding ) as avg_rate_3weeks,
    
    lag(Yds, 1, 0) over( partition by Name order by Week desc) as lag1_yds,
    lag(Yds, 2, 0) over( partition by Name order by Week desc) as lag2_yds,
    avg(Yds) over( partition by Name order by Week desc
    rows between 3 preceding and 1 preceding ) as avg_yds_3weeks
from base
