# advancedFunctions.py
# used to calculate projected box office revenue and predict awards


# calculate projected domestic box office revenue
def calculate_national_box_office(db, genre, actor, director, release):

    # average ticket price for years 2000-2025
    ticket_prices = [5.39, 5.65, 5.80, 6.03, 6.21, 6.41, 6.55, 6.88, 7.18, 7.50, 7.89, 7.93, 
                    7.96, 8.13, 8.17, 8.43, 8.65, 8.97, 9.11, 9.16, 9.18, 10.17, 10.53, 10.78, 11.31, 11.31]

    # define month ranges per quarter
    quarter_ranges = {
        "Q1": (1, 3),
        "Q2": (4, 6),
        "Q3": (7, 9),
        "Q4": (10, 12)
    }

    # start and end months for the quarter inputted 
    start_month, end_month = quarter_ranges[release]

    # query to find average box office revenue of the genre, actor and director
    #FIX THIS QUERY!!!!!!!!!!!!!!
    #query that finds movies with the actor or director in them, and movies with the matching genre and release quarter
    genreQuery = """
    SELECT DISTINCT M.id, M.title, B.domestic_revenue
    FROM MovieStatistics M
    JOIN BoxOffice B ON B.movie_id = M.id
    LEFT JOIN MembersAndAwards A ON M.id = A.movie_id
    LEFT JOIN DirectorsAndActors DA_actor 
    ON A.member_id = DA_actor.member_id AND DA_actor.roll_type = 'ACTOR'
    LEFT JOIN DirectorsAndActors DA_director 
    ON A.member_id = DA_director.member_id AND DA_director.roll_type = 'DIRECTOR'
    WHERE IFNULL(DA_actor.member_name,'') LIKE %s
   OR IFNULL(DA_director.member_name,'') LIKE %s
   UNION
   SELECT DISTINCT M.id, M.title, B.domestic_revenue
   FROM MovieStatistics M
   JOIN BoxOffice B ON B.movie_id = M.id
   WHERE LOWER(M.genres) LIKE LOWER(%s)
   AND YEAR(M.release_date) = %s
   AND MONTH(M.release_date) BETWEEN %s AND %s;
   """

    # Test values for your example movie
    cursor_blank = db.cursor(buffered=True)
    values = (
    f"%{hypothetical_actor}%",      # actor
    f"%{hypothetical_director}%",   # director
    f"%{hypothetical_genre}%",      # genre
    hypothetical_year,              # year
    hypothetical_quarter_start,     # start month
    hypothetical_quarter_end        # end month
    )
    
    cursor_blank.execute(genreQuery, values)
    #OR OR IFNULL(DA_actor.member_name,'') LIKE %s OR IFNULL(DA_director.member_name,'') LIKE %s
    #values = (f"%{genre}%", f"%{actor}%", f"%{director}%", start_month, end_month, 2019)
    results = cursor_blank.fetchall()
    print(f"Number of rows returned: {len(results)}")
    for row in results:
        print(row)

    # used as a counter for total number of tickets
    total_tickets_sold_genre = 0
    """
    for i in range(26): # iterates from 0 to 25, representing years after 2000

        # submit query and store average revenue
        cursor_revenue = db.cursor(buffered=True)
        values = (f"%{genre}%", start_month, end_month, 2000 + i)
        cursor_revenue.execute(genreQuery, values)
        result = cursor_revenue.fetchone()

        # defines avg_revenue if applicable, otherwise set zero
        if result and result[0] is not None:
            avg_revenue = float(result[0])  # convert to float for later division
            
        else:
            avg_revenue = 0  # default to 0 if no data found
            
        # find tickets sold for the year and add to total
        tickets_sold = avg_revenue / ticket_prices[i]
        total_tickets_sold_genre += tickets_sold

        cursor_revenue.close()"""

    # find average box office for movies with the same actor (has more impact) sort by genre and year
    
    # find average box office for movies with the same director (has smallest impact) sort by genre and year

# calculate projected foreign box office revenue
def calculate_foreign_box_office(genre, actor, director, release):
    return 0
    # Step one: calculate average foreign ticket price
    # Step two: calculate foreign box office
