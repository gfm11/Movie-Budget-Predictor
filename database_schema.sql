--build database schema here

--table 1
create table MovieStatistics (
    id int primary key,
    title varchar(120) not null,
    vote_average float,
    vote_count int,
    movie_status varchar(40) not null, --changed attribute title
    release_year int,
    revenue int,
    adult char(1), --changed datatype -> Y/N
    genres varchar(300) not null,
    
    check (release_year >= 2000)
);

--table 2
create table BoxOffice (
    movie_id int primary key,
    rank int, --removed duplicate title attribute
    worldwide_revenue float,
    domestic_revenue float,
    domestic_percentage float,

    foreign key (movie_id)
    references MovieStatistics(id)
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
);
