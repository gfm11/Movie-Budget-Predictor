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

    # used as a counter for total number of tickets
    total_tickets_sold_weighted = 0

    # used as a counter for total number of movies
    total_movies_matched_weighted = 0 

    # get total tickets sold and total movies matched from 2000-2025
    for i in range(26): # iterates from 0 to 25, representing years after 2000

        # holds returned values from SQL procedure
        avg_revenue = 0
        num_movies = 0

        # weights movies so newer movies have a larger effect than older ones, on a scale from 1.0 to 2.5
        weight = 1.0 + (i / 25) * 1.5

        # submit query and store average revenue
        cursor_avg_revenue = db.cursor(buffered=True)
        values = [actor, director, genre, 2000 + i, start_month, end_month, 0, 0]
        retvals = cursor_avg_revenue.callproc('averageDomesticRevenue', values)

        # defines avg_revenue if applicable, otherwise set zero
        if retvals and retvals[6] is not None:
            avg_revenue = float(retvals[6])  # convert to float for later division
            print("AVERAGE REVENUE: ", avg_revenue)
            
        if retvals and retvals[7] is not None:
            num_movies = float(retvals[7])
            print("NUMBER OF MOVIES: ", num_movies)
            
        # find tickets sold for the year and add to total
        tickets_sold = avg_revenue / ticket_prices[i]
        total_tickets_sold_weighted += tickets_sold * weight
        total_movies_matched_weighted += num_movies * weight
        

        cursor_avg_revenue.close()
    
    # calculate projected box office
    tickets_per_movie = total_tickets_sold_weighted / total_movies_matched_weighted
    projected_box_office = int(tickets_per_movie * ticket_prices[24])
    print("TICKETS SOLD: ", total_tickets_sold_weighted)
    print("MOVIES MATCHED: ", total_movies_matched_weighted)
    print("TICKS PER MOVIE: ", tickets_per_movie)
    print("PROJECTED BOX OFFICE: ", projected_box_office)

    return projected_box_office

# calculate projected foreign box office revenue
def calculate_foreign_box_office(db, genre, actor, director, release):
        # average ticket price for years 2000-2025
    ticket_prices = [5.27, 5.45, 5.80, 5.78, 5.98, 6.13, 6.36, 6.63, 6.88, 7.30, 7.88, 7.97, 
                    8.29, 8.56, 8.77, 9.29, 9.55, 8.97, 9.76, 9.43, 9.32, 8.91, 9.86, 10.11, 10.11, 10.38]

    # define month ranges per quarter
    quarter_ranges = {
        "Q1": (1, 3),
        "Q2": (4, 6),
        "Q3": (7, 9),
        "Q4": (10, 12)
    }

    # start and end months for the quarter inputted 
    start_month, end_month = quarter_ranges[release]

    # used as a counter for total number of tickets
    total_tickets_sold_weighted = 0

    # used as a counter for total number of movies
    total_movies_matched_weighted = 0 

    # get total tickets sold and total movies matched from 2000-2025
    for i in range(26): # iterates from 0 to 25, representing years after 2000

        # holds returned values from SQL procedure
        avg_revenue = 0
        num_movies = 0

        # weights movies so newer movies have a larger effect than older ones, on a scale from 1.0 to 2.5
        weight = 1.0 + (i / 25) * 1.5

        # submit query and store average revenue
        cursor_avg_revenue = db.cursor(buffered=True)
        values = [actor, director, genre, 2000 + i, start_month, end_month, 0, 0]
        retvals = cursor_avg_revenue.callproc('averageForeignRevenue', values)

        # defines avg_revenue if applicable, otherwise set zero
        if retvals and retvals[6] is not None:
            avg_revenue = float(retvals[6])  # convert to float for later division
            print("AVERAGE REVENUE: ", avg_revenue)
            
        if retvals and retvals[7] is not None:
            num_movies = float(retvals[7])
            print("NUMBER OF MOVIES: ", num_movies)
            
        # find tickets sold for the year and add to total
        tickets_sold = avg_revenue / ticket_prices[i]
        total_tickets_sold_weighted += tickets_sold * weight
        total_movies_matched_weighted += num_movies * weight
        

        cursor_avg_revenue.close()
    
    # calculate projected box office
    tickets_per_movie = total_tickets_sold_weighted / total_movies_matched_weighted
    projected_box_office = int(tickets_per_movie * ticket_prices[24])
    print("TICKETS SOLD: ", total_tickets_sold_weighted)
    print("MOVIES MATCHED: ", total_movies_matched_weighted)
    print("TICKS PER MOVIE: ", tickets_per_movie)
    print("PROJECTED BOX OFFICE: ", projected_box_office)

    return projected_box_office

def calculate_award_percentage(db, genre, actor, director, release):

    quarter_weights = {
        "Q1": 0.85, "Q2": 1.00, "Q3": 1.15, "Q4": 1.30   
    }

    quarter_weight = quarter_weights.get(release, 1.0)

    all_awards = 0

    for i in range(26):

        weight_fullmatch = 1.0 + (i / 25) * 1.5

        cursor_actor = db.cursor(buffered=True)
        ActorQuery = "SELECT IFNULL(SUM(member_awards), 0) FROM DirectorsAndActors WHERE member_name=%s AND roll_type='ACTOR'"
        cursor_actor.execute(ActorQuery, (actor,))
        actor_awards = cursor_actor.fetchone()[0]
        cursor_actor.close()

        cursor_director = db.cursor(buffered=True)
        DirectorQuery = "SELECT IFNULL(SUM(member_awards), 0) FROM DirectorsAndActors WHERE member_name=%s AND roll_type='DIRECTOR'"
        cursor_director.execute(DirectorQuery, (director,))
        director_awards = cursor_director.fetchone()[0]
        cursor_director.close()

        if actor_awards > director_awards:
            weight_actor = 1.0 + (i / 25) * 1.2
            weight_director = 1.0 + (i / 25)
        else:
            weight_actor = 1.0 + (i / 25)
            weight_director = 1.0 + (i / 25) * 1.2

        cursor = db.cursor(buffered=True)
        values = [actor, director, genre, 2000 + i, 0]
        projected_Awards = cursor.callproc('averageAwardPerformance', values)

        avg_awards = float(projected_Awards[4]) if projected_Awards[4] else 0.0

        values_actor = [actor, "", genre, 2000 + i, 0]
        projected_Awards_actor = cursor.callproc('averageAwardPerformance', values_actor)

        avg_awards_actor = float(projected_Awards_actor[4]) if projected_Awards_actor[4] else 0.0

        values_director = ["", director, genre, 2000 + i, 0]
        projected_Awards_director = cursor.callproc('averageAwardPerformance', values_director)

        avg_awards_director = float(projected_Awards_director[4]) if projected_Awards_director[4] else 0.0
        cursor.close()

        combined = ((avg_awards * weight_fullmatch + avg_awards_actor * weight_actor + avg_awards_director * weight_director) / 3) * quarter_weight

        all_awards += combined

    cursor = db.cursor(buffered=True)
    cursor.execute("SELECT MAX(movie_awards) FROM MembersAndAwards")
    max_awards = cursor.fetchone()[0] or 1
    cursor.close()

    percentage = min(100, (all_awards / max_awards) * 100)

    return round(percentage, 2)
