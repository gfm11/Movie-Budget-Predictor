# advancedFunctions.py
# used to calculate projected box office revenue and predict awards


# calculate projected box office revenue
def calculate_box_office(db, genre, actor, director, release):
    # average US ticket price for years 2000-2025
    domestic_ticket_prices = [5.39, 5.65, 5.80, 6.03, 6.21, 6.41, 6.55, 6.88, 7.18, 7.50, 7.89, 7.93, 
                    7.96, 8.13, 8.17, 8.43, 8.65, 8.97, 9.11, 9.16, 9.18, 10.17, 10.53, 10.78, 11.31, 11.31]
    
    # average foreign ticket price for years 2000-2025
    foreign_ticket_prices = [5.27, 5.45, 5.80, 5.78, 5.98, 6.13, 6.36, 6.63, 6.88, 7.30, 7.88, 7.97, 
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
    domestic_total_tickets_sold_weighted = 0
    foreign_total_tickets_sold_weighted = 0

    # used as a counter for total number of movies
    total_movies_matched_weighted = 0 

    # get total tickets sold and total movies matched from 2000-2025
    for i in range(26): # iterates from 0 to 25, representing years after 2000

        # holds returned values from SQL procedure
        avg_domestic_revenue = 0
        avg_foreign_revenue = 0
        num_movies = 0

        # weights movies so newer movies have a larger effect than older ones, on a scale from 1.0 to 2.5
        weight = 1.0 + (i / 25) * 1.5

        # submit query and store average revenue
        cursor_avg_revenue = db.cursor(buffered=True)
        values = [actor, director, genre, 2000 + i, start_month, end_month, 0, 0, 0]
        retvals = cursor_avg_revenue.callproc('averageRevenue', values)

        # defines avg_domestic_revenue if applicable, otherwise set zero
        if retvals and retvals[6] is not None:
            avg_domestic_revenue = float(retvals[6])  # convert to float for later division
            print("AVERAGE DOMESTIC REVENUE: ", avg_domestic_revenue)

        # defines avg_foreign_revenue if applicable, otherwise set zero
        if retvals and retvals[8] is not None:
            avg_foreign_revenue = float(retvals[8])  # convert to float for later division
            print("AVERAGE FOREIGN REVENUE: ", avg_foreign_revenue)
            
        if retvals and retvals[7] is not None:
            num_movies = float(retvals[7])
            print("NUMBER OF MOVIES: ", num_movies)
            
        # find domestic tickets sold for the year and add to total
        D_tickets_sold = avg_domestic_revenue / domestic_ticket_prices[i]
        domestic_total_tickets_sold_weighted += D_tickets_sold * weight

        # find foreign tickets sold for the year and add to total
        F_tickets_sold = avg_foreign_revenue / foreign_ticket_prices[i]
        foreign_total_tickets_sold_weighted += F_tickets_sold * weight

        # add weighted movies matched to total
        total_movies_matched_weighted += num_movies * weight

        cursor_avg_revenue.close()

    # return -1 if no movies could be matched
    if total_movies_matched_weighted <= 0:
        return -1

    # calculate projected box office
    D_tickets_per_movie = domestic_total_tickets_sold_weighted / total_movies_matched_weighted
    D_projected_box_office = int(D_tickets_per_movie * domestic_ticket_prices[24])
    F_tickets_per_movie = foreign_total_tickets_sold_weighted / total_movies_matched_weighted
    F_projected_box_office = int(F_tickets_per_movie * foreign_ticket_prices[24])

    # output used to see what the function is doing
    print("DOMESTIC TICKETS SOLD: ", domestic_total_tickets_sold_weighted)
    print("FOREIGN TICKETS SOLD: ", foreign_total_tickets_sold_weighted)
    print("MOVIES MATCHED: ", total_movies_matched_weighted)
    print("TICKS PER MOVIE: ", D_tickets_per_movie)
    print("FOREIGN TICKS PER MOVIE: ", F_tickets_per_movie)
    print("PROJECTED DOMESTIC BOX OFFICE: ", D_tickets_per_movie)
    print("PROJECTED FOREIGN BOX OFFICE: ", F_projected_box_office)

    # return projected values
    projected_values = [f"{D_projected_box_office:,}", f"{F_projected_box_office:,}"]
    return projected_values

def movie_similarity(new_genre, new_actor, new_director, row):
    score = 0

    if new_genre in (row["genres"] or ""):
        score += 2

    if row["actors"] and new_actor in row["actors"].split(','):
        score += 3

    if row["directors"] and new_director in row["directors"].split(','):
        score += 3

    return score

def knn_predict_awards(db, genre, actor, director, k):
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            ms.id AS movie_id,
            ms.genres,
            GROUP_CONCAT(CASE WHEN da.roll_type = 'ACTOR' THEN da.member_name END SEPARATOR ',') AS actors,
            GROUP_CONCAT(CASE WHEN da.roll_type = 'DIRECTOR' THEN da.member_name END SEPARATOR ',') AS directors,
            MAX(ma.movie_awards) AS awards
        FROM MovieStatistics ms
        LEFT JOIN MembersAndAwards ma ON ms.id = ma.movie_id
        LEFT JOIN DirectorsAndActors da ON ma.member_id = da.member_id
        GROUP BY ms.id
    """)

    rows = cursor.fetchall()
    cursor.close()

    scored = []
    for r in rows:
        sim = movie_similarity(genre, actor, director, r)
        scored.append((sim, r["awards"] or 0))

    scored.sort(reverse=True, key=lambda x: x[0])

    top = [x for x in scored if x[0] > 0][:k]

    if not top:
        return 0

    total_sim = sum(s for s, _ in top)
    knn_score = sum(s * a for s, a in top) / total_sim
    return knn_score


def calculate_award_percentage(db, genre, actor, director, release):

    quarter_weights = {"Q1":0.85,"Q2":1.0,"Q3":1.15,"Q4":1.30}
    quarter_weight = quarter_weights.get(release, 1.0)

    weight_fullmatch = 1.5

    cursor = db.cursor(buffered=True)

    cursor.execute("SELECT IFNULL(SUM(member_awards), 0) FROM DirectorsAndActors WHERE member_name=%s AND roll_type='ACTOR'", (actor,))
    actor_awards = cursor.fetchone()[0]

    cursor.execute("SELECT IFNULL(SUM(member_awards), 0) FROM DirectorsAndActors WHERE member_name=%s AND roll_type='DIRECTOR'", (director,))
    director_awards = cursor.fetchone()[0]

    if actor_awards > director_awards:
        weight_actor = 1.2
        weight_director = 1.0
    else:
        weight_actor = 1.0 
        weight_director = 1.2

    values = [actor, director, genre, 0, 0]
    projected_Awards = cursor.callproc('averageAwardPerformance', values)
    avg_awards = float(projected_Awards[4]) if projected_Awards[4] else 0.0

    cursor.execute("""SELECT AVG(MA.movie_awards) 
                    FROM MembersAndAwards MA JOIN DirectorsAndActors DA ON DA.member_id = MA.member_id
                    WHERE DA.member_name = %s  AND DA.roll_type = 'ACTOR'""", (actor,))
    row = cursor.fetchone()
    avg_awards_actor = float(row[0]) if row and row[0] is not None else 0.0

    cursor.execute("""SELECT AVG(MA.movie_awards)
                    FROM MembersAndAwards MA JOIN DirectorsAndActors DA ON DA.member_id = MA.member_id
                    WHERE DA.member_name = %s AND DA.roll_type = 'DIRECTOR'""", (director,))
    row = cursor.fetchone()
    avg_awards_director = float(row[0]) if row and row[0] is not None else 0.0

    cursor.close()

    combined = (
        avg_awards * weight_fullmatch +
        avg_awards_actor * weight_actor +
        avg_awards_director * weight_director
    ) / 3.0

    all_awards = combined + float(avg_awards_actor) + float(avg_awards_director)

    knn_estimate = knn_predict_awards(db, genre, actor, director, k=5)

    final_awards = (all_awards * 0.70) + (knn_estimate * 0.30)

    if (final_awards == 0):
        final_awards = float(actor_awards) + float(director_awards)
    
    final_awards *= quarter_weight

    percentage = (final_awards / 163) * 100
    if percentage > 100:
        percentage = 99.6
    return round(percentage, 2)
