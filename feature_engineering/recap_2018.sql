drop table if exists passing_2018;

create table passing_2018 (
    Player text,
    Team text,
    yds_game real,
    TDs real,
    Ints real,
    Rate real,
    ppg real,
    td_per_game real,
    int_per_game real
);

drop table if exists rushing_2018;

create table rushing_2018 (
    Player text,
    Team text,
    yds_game real,
    TDs real,
    FUMs real,
    ppg real,
    td_per_game real,
    fum_per_game real
);

drop table if exists receiving_2018;

create table receiving_2018 (
    Player text,
    Team text,
    yds_game real,
    TDs real,
    FUMs real,
    ppg real,
    td_per_game real,
    int_per_game real
);

-- insert summary data into the various tables

insert into passing_2018
select Player, 
    Team,
    `Yds/G` as yds_game,
    cast(TD as float) as TDs,
    cast(`Int` as float) as Ints,
    Rate,
    `2018_ppg` as ppg,
    cast(TD as float)/16 as td_per_game,
    cast(`Int` as float)/16 as int_per_game
from `2018_passing_recap`;

insert into rushing_2018
select 
    Player, 
    Team,
    `Yds/G` as yds_game,
    cast(TD as real) as TDs,
    cast(FUM as real) as FUMs,
    `2018_ppg` as ppg,
    cast(TD as real)/16 as td_per_game,
    cast(FUM as real)/16 as fum_per_game
from `2018_rushing_recap`;


insert into receiving_2018
select 
    Player, 
    Team,
    `Yds/G` as yds_game,
    cast(TD as real) as TDs,
    cast(FUM as real) as FUMs,
    `2018_ppg` as ppg,
    cast(TD as real)/16 as td_per_game,
    cast(FUM as real)/16 as fum_per_game
from `2018_receiving_recap`;