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

create table if not exists Users (
    user_id int auto_increment primary key,
    username varchar(50) unique not null,
    hashed_password varchar(255) not null
);

create table if not exists UserMovies (
    user_id int,
    movie_id int,
    primary key(user_id, movie_id),

    foreign key (movie_id)
        references MovieStatistics(id)
        on delete cascade
        on update cascade,

    foreign key (user_id)
        references Users(user_id)
        on delete cascade
        on update cascade
);

-- making sure this procedure is not already defined before trying to use it
DROP PROCEDURE IF EXISTS averageDomesticRevenue;

-- changing delimiter so ; can be used inside the procedure
DELIMITER $$

-- procedure for retrieving movies for domestic box office predictor advanced function
-- selects revenue from movies with matching genre, actor, or director input, and matching year and quarter input
-- returns average revenue from those movies and count of movies used in the calculation
CREATE PROCEDURE averageDomesticRevenue(IN input_actor VARCHAR(255), IN input_director VARCHAR(255), IN input_genre VARCHAR(255),
                                           IN input_year INT, IN input_quarter_start INT, IN input_quarter_end INT, 
                                           OUT avg_revenue FLOAT, OUT movie_count FLOAT)
BEGIN
    SELECT IFNULL(AVG(domestic_revenue), 0)
    INTO avg_revenue
    FROM (
        SELECT DISTINCT M.title, B.domestic_revenue
        FROM MovieStatistics M
        JOIN BoxOffice B ON B.movie_id = M.id
        LEFT JOIN MembersAndAwards MA_actor 
            ON MA_actor.movie_id = M.id
        LEFT JOIN DirectorsAndActors DA_actor 
            ON DA_actor.member_id = MA_actor.member_id AND DA_actor.roll_type = 'ACTOR'
        LEFT JOIN MembersAndAwards MA_director 
            ON MA_director.movie_id = M.id
        LEFT JOIN DirectorsAndActors DA_director 
            ON DA_director.member_id = MA_director.member_id AND DA_director.roll_type = 'DIRECTOR'
        WHERE YEAR(M.release_date) = input_year
        AND MONTH(M.release_date) BETWEEN input_quarter_start AND input_quarter_end
        AND (input_genre = '' OR LOWER(M.genres) LIKE LOWER(CONCAT('%', input_genre, '%')))
        AND (input_actor = '' OR DA_actor.member_name LIKE CONCAT('%', input_actor, '%'))
        AND (input_director = '' OR DA_director.member_name LIKE CONCAT('%', input_director, '%'))
    ) AS unique_movies;

    SELECT IFNULL(COUNT(*), 0)
    INTO movie_count
    FROM (
        SELECT DISTINCT M.title, B.domestic_revenue
        FROM MovieStatistics M
        JOIN BoxOffice B ON B.movie_id = M.id
        LEFT JOIN MembersAndAwards MA_actor 
            ON MA_actor.movie_id = M.id
        LEFT JOIN DirectorsAndActors DA_actor 
            ON DA_actor.member_id = MA_actor.member_id AND DA_actor.roll_type = 'ACTOR'
        LEFT JOIN MembersAndAwards MA_director 
            ON MA_director.movie_id = M.id
        LEFT JOIN DirectorsAndActors DA_director 
            ON DA_director.member_id = MA_director.member_id AND DA_director.roll_type = 'DIRECTOR'
        WHERE YEAR(M.release_date) = input_year
        AND MONTH(M.release_date) BETWEEN input_quarter_start AND input_quarter_end
        AND (input_genre = '' OR LOWER(M.genres) LIKE LOWER(CONCAT('%', input_genre, '%')))
        AND (input_actor = '' OR DA_actor.member_name LIKE CONCAT('%', input_actor, '%'))
        AND (input_director = '' OR DA_director.member_name LIKE CONCAT('%', input_director, '%'))
    ) AS unique_movies_count;
END$$

DELIMITER ;

DELIMITER $$

DROP TABLE IF EXISTS averageForeignRevenue;

-- procedure for retrieving movies for foreign box office predictor advanced function
-- selects revenue from movies with matching genre, actor, or director input, and matching year and quarter input
-- returns average revenue from those movies and count of movies used in the calculation
DELIMITER $$
CREATE PROCEDURE averageForeignRevenue(IN input_actor VARCHAR(255), IN input_director VARCHAR(255), IN input_genre VARCHAR(255),
                                           IN input_year INT, IN input_quarter_start INT, IN input_quarter_end INT, 
                                           OUT avg_revenue FLOAT, OUT movie_count FLOAT)
BEGIN
    SELECT IFNULL(AVG(worldwide_revenue - domestic_revenue), 0)
    INTO avg_revenue
    FROM (
        SELECT DISTINCT M.title, B.worldwide_revenue, B.domestic_revenue
        FROM MovieStatistics M
        JOIN BoxOffice B ON B.movie_id = M.id
        LEFT JOIN MembersAndAwards MA_actor 
            ON MA_actor.movie_id = M.id
        LEFT JOIN DirectorsAndActors DA_actor 
            ON DA_actor.member_id = MA_actor.member_id AND DA_actor.roll_type = 'ACTOR'
        LEFT JOIN MembersAndAwards MA_director 
            ON MA_director.movie_id = M.id
        LEFT JOIN DirectorsAndActors DA_director 
            ON DA_director.member_id = MA_director.member_id AND DA_director.roll_type = 'DIRECTOR'
        WHERE YEAR(M.release_date) = input_year
        AND MONTH(M.release_date) BETWEEN input_quarter_start AND input_quarter_end
        AND (input_genre = '' OR LOWER(M.genres) LIKE LOWER(CONCAT('%', input_genre, '%')))
        AND (input_actor = '' OR DA_actor.member_name LIKE CONCAT('%', input_actor, '%'))
        AND (input_director = '' OR DA_director.member_name LIKE CONCAT('%', input_director, '%'))
    ) AS unique_movies;

    SELECT IFNULL(COUNT(*), 0)
    INTO movie_count
    FROM (
        SELECT DISTINCT M.title, B.worldwide_revenue, B.domestic_revenue
        FROM MovieStatistics M
        JOIN BoxOffice B ON B.movie_id = M.id
        LEFT JOIN MembersAndAwards MA_actor 
            ON MA_actor.movie_id = M.id
        LEFT JOIN DirectorsAndActors DA_actor 
            ON DA_actor.member_id = MA_actor.member_id AND DA_actor.roll_type = 'ACTOR'
        LEFT JOIN MembersAndAwards MA_director 
            ON MA_director.movie_id = M.id
        LEFT JOIN DirectorsAndActors DA_director 
            ON DA_director.member_id = MA_director.member_id AND DA_director.roll_type = 'DIRECTOR'
        WHERE YEAR(M.release_date) = input_year
        AND MONTH(M.release_date) BETWEEN input_quarter_start AND input_quarter_end
        AND (input_genre = '' OR LOWER(M.genres) LIKE LOWER(CONCAT('%', input_genre, '%')))
        AND (input_actor = '' OR DA_actor.member_name LIKE CONCAT('%', input_actor, '%'))
        AND (input_director = '' OR DA_director.member_name LIKE CONCAT('%', input_director, '%'))
    ) AS unique_movies_count;
END$$

DELIMITER ;
