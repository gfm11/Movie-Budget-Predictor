-- SQL setup for Movie Budget Predictor database

CREATE DATABASE IF NOT EXISTS moviebudgetpredictor;
USE moviebudgetpredictor;

CREATE TABLE IF NOT EXISTS MovieStatistics (
    id INT PRIMARY KEY,
    title VARCHAR(300) NOT NULL,
    vote_average FLOAT,
    vote_count INT,
    movie_status VARCHAR(40) NOT NULL,
    release_date DATE,
    revenue BIGINT,
    adult CHAR(1),
    genres VARCHAR(300),
    CHECK (release_date >= '2000-01-01'),
    CHECK (adult IN ('Y', 'N'))
);

create table if not exists BoxOffice (
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

create table if not exists DirectorsAndActors (
    member_id int primary key auto_increment,
    member_name varchar(300) not null,
    roll_type varchar(8) not null,
    member_awards int default 0,

    check (roll_type in ('ACTOR', 'DIRECTOR'))
);


create table if not exists MembersAndAwards (
    movie_id int,
    member_id int,
    movie_awards int,

    primary key (movie_id, member_id),

    foreign key (movie_id)
    references MovieStatistics(id)
    on delete cascade
    on update cascade,

    foreign key (member_id)
    references DirectorsAndActors(member_id)
    on delete cascade
    on update cascade 
);
