--command log for creating MySQL database

--start mysql in terminal
sudo service mysql start

--login as root
mysql -u root -p

--create and/or use database
create database moviebudgetpredictor;
use moviebudgetpredictor;

--create tables within database
--table 1
create table MovieStatistics (
    id int primary key,
    title varchar(300) not null,
    vote_average float,
    vote_count int,
    movie_status varchar(40) not null,
    release_date date,
    revenue bigint,
    adult char(1),
    genres varchar(300),
    
    check (release_date >= '2000-01-01')
);

--table 2
create table BoxOffice (
    movie_id int primary key,
    title varchar(120) not null,
    movie_rank int,
    worldwide_revenue float,
    domestic_revenue float,
    domestic_percentage float,

    foreign key (movie_id)
    references MovieStatistics(id)
    on delete cascade
    on update cascade 
);

--table 3
create table MembersAndAwards (
    movie_id int primary key,
    directors varchar(300) not null,
    cast_members varchar(300) not null,
    actor_awards int,
    director_awards int,
    movie_awards int,

    foreign key (movie_id)
    references MovieStatistics(id)
    on delete cascade
    on update cascade 
);
