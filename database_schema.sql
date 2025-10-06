--build database schema here

--table 1
create table MovieStatistics (
    id int primary key
    title varchar(120) not null
    vote_average float
    vote_count int
    movie_status varchar(40) not null --changed attribute title
    release_year int
    revenue int
    adult char(1) --changed datatype -> Y/N
    generes varchar(300) not null
    
    check (release_year >= 2000)
);