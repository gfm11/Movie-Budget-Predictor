# advancedFunctions.py
# used to calculate projected box office revenue and predict awards


# calculate projected domestic box office revenue
def calculate_national_box_office(db, genre, actor, director, release):
    # ADD COUNTER FOR NUMBER OF MOVIES PULLED BY QUERY!!!!!

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
    total_tickets_sold = 0

    # used as a counter for total number of movies
    total_movies_matched = 0 

    # get total tickets sold and total movies matched from 2000-2025
    for i in range(26): # iterates from 0 to 25, representing years after 2000

        # holds returned values from SQL procedure
        avg_revenue = 0
        num_movies = 0

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
        total_tickets_sold += tickets_sold
        total_movies_matched += num_movies
        

        cursor_avg_revenue.close()
    
    print("TICKETS SOLD: ", total_tickets_sold)



# calculate projected foreign box office revenue
def calculate_foreign_box_office(genre, actor, director, release):
    return 0
    # Step one: calculate average foreign ticket price
    # Step two: calculate foreign box office
