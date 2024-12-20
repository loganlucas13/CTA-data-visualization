#
# Logan Lucas
# CS 341
# Project 1 - CTA Database App
# Spring 2024
#

import sqlite3
import matplotlib.pyplot as plt


##################################################################  
#
# print_stats
#
# Given a connection to the CTA database, executes various
# SQL queries to retrieve and output basic stats.
#
def print_stats(dbConn):
    dbCursor = dbConn.cursor()
    
    print("General Statistics:")
    
    # number of stations
    dbCursor.execute("Select count(*) From Stations;")
    row = dbCursor.fetchone()
    print("  # of stations:", f"{row[0]:,}")

    # number of stops
    dbCursor.execute("SELECT count(*) FROM Stops;")
    row = dbCursor.fetchone()
    print("  # of stops:", f"{row[0]:,}")

    # number of ride entries
    dbCursor.execute("SELECT count(*) FROM Ridership;")
    row = dbCursor.fetchone()
    print("  # of ride entries:", f"{row[0]:,}")

    # date range
    dbCursor.execute("""SELECT * FROM (SELECT strftime("%Y-%m-%d", Ride_Date) FROM Ridership ORDER BY Ride_Date ASC LIMIT 1);""")
    startDate = dbCursor.fetchone()
    dbCursor.execute("""SELECT * FROM (SELECT strftime("%Y-%m-%d", Ride_Date) FROM Ridership ORDER BY Ride_Date DESC LIMIT 1);""")
    endDate = dbCursor.fetchone()

    print("  date range:", f"{startDate[0]} - {endDate[0]}")

    # total ridership (number of riders)
    dbCursor.execute("SELECT sum(Num_Riders) FROM Ridership;")
    row = dbCursor.fetchone()
    print("  Total ridership: ", f"{row[0]:,}")
    

# brief: finds all station names that match the user input (% and _ are allowed)
# param: dbConn - connection to database
# return: none
def Command1(dbConn):
    dbCursor = dbConn.cursor()

    print()

    search = input("Enter partial station name (wildcards _ and %): ")

    query = "SELECT Station_ID, Station_Name FROM Stations WHERE Station_Name LIKE (?) ORDER BY Station_Name ASC"
    dbCursor.execute(query, (search,)) # inserts the user input into search query and executes
    matches = dbCursor.fetchall()

    if (len(matches) == 0):
        print("**No stations found...")
    else:
        for i in range(0, len(matches)):
            print("{} : {}".format(*matches[i]))
    
    print()
       
       
# brief: finds distribution of riders on days of the week
# param: dbConn - connection to database
# return: none
def Command2(dbConn):
    dbCursor = dbConn.cursor()

    print()

    search = input("Enter the name of the station you would like to analyze: ")

    checkStationQuery = "SELECT count(*) FROM Stations WHERE Station_Name = (?);"
    dbCursor.execute(checkStationQuery, (search,))

    if dbCursor.fetchone()[0] == 0: # checks if a station matches the user's search
        print("**No data found...")
    else:
        query = """SELECT sum(Num_Riders) FROM Stations
        JOIN Ridership ON Stations.Station_ID = Ridership.Station_ID 
        WHERE Type_of_Day = (?) AND Station_Name = (?);"""
        
        dbCursor.execute(query, ('W', search))
        weekdayRidership = dbCursor.fetchone()

        dbCursor.execute(query, ('A', search))
        saturdayRidership = dbCursor.fetchone()

        dbCursor.execute(query, ('U', search))
        sundayOrHolidayRidership = dbCursor.fetchone()

        totalRidership = weekdayRidership[0] + saturdayRidership[0] + sundayOrHolidayRidership[0];

        print("Percentage of ridership for the {} station:".format(search))
        print("  Weekday ridership:", f"{weekdayRidership[0]:,}", f"({(weekdayRidership[0]/totalRidership)*100:.2f}%)")
        print("  Saturday ridership:", f"{saturdayRidership[0]:,}", f"({(saturdayRidership[0]/totalRidership)*100:.2f}%)")
        print("  Sunday/holiday ridership:", f"{sundayOrHolidayRidership[0]:,}", f"({(sundayOrHolidayRidership[0]/totalRidership)*100:.2f}%)")
        print("  Total ridership:", f"{totalRidership:,}")
    
    print()


# brief: outputs the total ridership on weekdays for each station (with station names)
# param: dbConn - connection to database
# return: none
def Command3(dbConn):
    dbCursor = dbConn.cursor()

    query = """SELECT Station_Name, sum(Num_Riders) as Total_Riders FROM Stations
    JOIN Ridership ON Stations.Station_ID = Ridership.Station_ID
    WHERE Type_of_Day = 'W'
    GROUP BY Station_Name
    ORDER BY Total_Riders DESC;"""

    dbCursor.execute(query)
    results = dbCursor.fetchall()

    totalRidership = 0
    for i in range(0, len(results)):
        totalRidership += results[i][1]
    
    print("Ridership on Weekdays for Each Station")
    for i in range(0, len(results)):
        print("{} : {:,} ({:.2f}%)".format(*results[i], (results[i][1]/totalRidership)*100))
    
    print()
    

# brief: outputs all stops given a line color and direction
# param: dbConn - connection to database
# return: none
def Command4(dbConn):
    dbCursor = dbConn.cursor()

    print()

    colorSearch = input("Enter a line color (e.g. Red or Yellow): ")

    checkColorQuery = "SELECT count(*) FROM Lines WHERE Color = (?) COLLATE NOCASE;"

    dbCursor.execute(checkColorQuery, (colorSearch,))

    if dbCursor.fetchone()[0] == 0:
        print("**No such line...\n")
        return
    
    directionSearch = input("Enter a direction (N/S/W/E): ")
    checkDirectionQuery = """SELECT count(*) FROM Stops
    JOIN StopDetails ON Stops.Stop_ID = StopDetails.Stop_ID
    JOIN Lines ON StopDetails.Line_ID = Lines.Line_ID
    WHERE Color = (?) COLLATE NOCASE AND Direction = (?) COLLATE NOCASE;"""

    dbCursor.execute(checkDirectionQuery, (colorSearch, directionSearch,))

    if dbCursor.fetchone()[0] == 0:
        print("**That line does not run in the direction chosen...\n")
        return
    
    finalQuery = """SELECT Stop_Name, ADA FROM Stations
    JOIN Stops ON Stations.Station_ID = Stops.Station_ID
    JOIN StopDetails ON Stops.Stop_ID = StopDetails.Stop_ID
    JOIN Lines ON StopDetails.Line_ID = Lines.Line_ID
    WHERE Color = (?) COLLATE NOCASE AND Direction = (?) COLLATE NOCASE
    ORDER BY Stop_Name ASC;"""

    dbCursor.execute(finalQuery, (colorSearch, directionSearch,))
    results = dbCursor.fetchall()

    for i in range(0, len(results)):
        if results[i][1] == 1:
            handicapOutput = "handicap accessible"
        else:
            handicapOutput = "not handicap accessible"
        
        print("{} : direction = {} ({})".format(results[i][0], directionSearch.upper(), handicapOutput))
    
    print()

    
# brief: outputs number of stops for each line color separated by direction
# param: dbConn - connection to database
# return: none
def Command5(dbConn):
    dbCursor = dbConn.cursor()

    totalStopQuery = """SELECT count(Stop_Name) FROM STOPS;"""
    dbCursor.execute(totalStopQuery)
    totalStops = dbCursor.fetchone()

    query = """SELECT Color, Direction, count(Stop_Name) FROM Stops
    JOIN StopDetails ON Stops.Stop_ID = StopDetails.Stop_ID
    JOIN Lines ON StopDetails.Line_ID = Lines.Line_ID
    GROUP BY Color, Direction
    ORDER BY Color ASC, Direction ASC;"""

    dbCursor.execute(query)
    results = dbCursor.fetchall()

    print("Number of Stops For Each Color By Direction")
    for i in range(0, len(results)):
        print("{} going {} : {} ({:.2f}%)".format(results[i][0], results[i][1], results[i][2], (results[i][2]/totalStops[0])*100))
    
    print()


# brief: outputs the total ridership for each year given a station name; also has the ability to plot the data
# param: dbConn - connection to database
# return: none
def Command6(dbConn):
    dbCursor = dbConn.cursor()

    print()

    search = input("Enter a station name (wildcards _ and %): ")

    checkStationQuery = """SELECT Station_Name FROM Stations WHERE Station_Name LIKE (?);"""
    dbCursor.execute(checkStationQuery, (search,))

    stationMatch = dbCursor.fetchall()

    if len(stationMatch) == 1:
        print("Yearly Ridership at {}".format(*stationMatch[0]))
    elif len(stationMatch) > 1:
        print("**Multiple stations found...\n")
        return
    else:
        print("**No station found...\n")
        return

    finalQuery = """SELECT strftime("%Y", Ride_Date) as Year, sum(Num_Riders) FROM Ridership
    JOIN Stations ON Ridership.Station_ID = Stations.Station_ID
    WHERE Station_Name LIKE (?)
    GROUP BY Year
    ORDER BY Year ASC;"""

    dbCursor.execute(finalQuery, (search,))
    results = dbCursor.fetchall()

    for i in range(0, len(results)):
        print("{} : {:,}".format(results[i][0], results[i][1]))
    
    print()

    toPlot = input("Plot? (y/n) ")

    print()

    if toPlot != 'y':
        return
    
    years, riderCount = zip(*results) # for plotting

    plt.plot(years, riderCount)
    plt.xlabel("Year")
    plt.ylabel("Number of Riders")
    plt.title("Yearly ridership at {}".format(*stationMatch[0]))
    plt.show()
        

# brief: outputs the total ridership for each month in a year given a station name and a year; can also plot
# param: dbConn - connection to database
# return: none
def Command7(dbConn):
    dbCursor = dbConn.cursor()

    print()

    search = input("Enter a station name (wildcards _ and %): ")

    checkStationQuery = """SELECT Station_Name FROM Stations WHERE Station_Name LIKE (?);"""
    dbCursor.execute(checkStationQuery, (search,))

    stationMatch = dbCursor.fetchall()

    if len(stationMatch) == 1:
        year = input("Enter a year: ")
        print("Monthly Ridership at {} for {}".format(*stationMatch[0], year))
    elif len(stationMatch) > 1:
        print("**Multiple stations found...\n")
        return
    else:
        print("**No station found...\n")
        return
    
    finalQuery = """SELECT strftime("%m/%Y", Ride_Date) AS Date, sum(Num_Riders) FROM Stations
    JOIN Ridership ON Stations.Station_ID = Ridership.Station_ID
    WHERE Station_Name LIKE (?) AND strftime("%Y", Ride_Date) = (?)
    GROUP BY Date
    ORDER BY Date ASC"""

    dbCursor.execute(finalQuery, (*stationMatch[0], year))
    results = dbCursor.fetchall()

    for i in range(0, len(results)):
        print("{} : {:,}".format(results[i][0], results[i][1]))
    
    toPlot = input("Plot? (y/n) ")

    print()

    if toPlot != 'y':
        return
    
    if (len(results) == 2): # to fix error when results has no data
        months, riderCount = zip(*results)
        plt.plot(months, riderCount)
        plt.xlabel("Month")
        plt.ylabel("Number of Riders")
        plt.title("Monthly Ridership at {} ({})".format(*stationMatch[0], year))
        plt.show()


# brief: outputs the first and last 5 days of ridership for two stations and plots the data
# param: dbConn - connection to database
# return: none
def Command8(dbConn):
    dbCursor = dbConn.cursor()

    print()

    year = input("Year to compare against? ")

    print()

    station1 = input("Enter station 1 (wildcards _ and %): ")

    checkStationQuery = """SELECT Station_Name FROM Stations WHERE Station_Name LIKE (?);"""
    dbCursor.execute(checkStationQuery, (station1,))

    station1Match = dbCursor.fetchall()

    if len(station1Match) > 1:
        print("**Multiple stations found...\n")
        return
    elif len(station1Match) < 1:
        print("**No station found...\n")
        return
    
    print()

    station2 = input("Enter station 2 (wildcards _ and %): ")

    dbCursor.execute(checkStationQuery, (station2,))

    station2Match = dbCursor.fetchall()

    if len(station2Match) > 1:
        print("**Multiple stations found...\n")
        return
    elif len(station2Match) < 1:
        print("**No station found...\n")
        return

    stationTitleQuery = """SELECT Station_ID, Station_Name FROM Stations
    WHERE Station_Name LIKE (?)"""

    dbCursor.execute(stationTitleQuery, (station1,))
    station1Title = dbCursor.fetchall()

    dbCursor.execute(stationTitleQuery, (station2, ))
    station2Title = dbCursor.fetchall()

    stationDataQuery = """
    SELECT * FROM 
    (SELECT strftime("%Y-%m-%d", Ride_Date) AS Formatted_Date, Num_Riders
        FROM Stations
        JOIN Ridership ON Stations.Station_ID = Ridership.Station_ID
        WHERE Station_Name LIKE ? AND strftime("%Y", Ride_Date) = ?
        GROUP BY Ride_Date
        ORDER BY Ride_Date ASC
        LIMIT 5)
    UNION
    SELECT * FROM 
    (SELECT strftime("%Y-%m-%d", Ride_Date) AS Formatted_Date, Num_Riders
        FROM Stations
        JOIN Ridership ON Stations.Station_ID = Ridership.Station_ID
        WHERE Station_Name LIKE ? AND strftime("%Y", Ride_Date) = ?
        GROUP BY Ride_Date
        ORDER BY Ride_Date DESC
        LIMIT 5)
    ORDER BY Formatted_Date ASC;
    """

    dbCursor.execute(stationDataQuery, (station1, year, station1, year))
    station1Data = dbCursor.fetchall()

    dbCursor.execute(stationDataQuery, (station2, year, station2, year))
    station2Data = dbCursor.fetchall()

    print("Station 1: {} {}".format(station1Title[0][0], station1Title[0][1]))
    for i in range(0, len(station1Data)):
        print("{} {}".format(station1Data[i][0], station1Data[i][1]))
    
    print("Station 2: {} {}".format(station2Title[0][0], station2Title[0][1]))
    for i in range(0, len(station2Data)):
        print("{} {}".format(station2Data[i][0], station2Data[i][1]))

    print()

    toPlot = input("Plot? (y/n) ")

    print()

    if toPlot != 'y':
        return
    

    stationPlottingQuery = """SELECT ROW_NUMBER() OVER(ORDER BY Ride_Date) as Day_Number, Num_Riders
    FROM Stations
    JOIN Ridership ON Stations.Station_ID = Ridership.Station_ID
    WHERE Station_Name LIKE ? AND strftime("%Y", Ride_Date) = ?
    GROUP BY Ride_Date
    ORDER BY Ride_Date ASC;"""

    dbCursor.execute(stationPlottingQuery, (station1, year))
    station1PlotData = dbCursor.fetchall()

    dbCursor.execute(stationPlottingQuery, (station2, year))
    station2PlotData = dbCursor.fetchall()

    station1days, station1data = zip(*station1PlotData)
    station2days, station2data = zip(*station2PlotData)

    plt.plot(station1days, station1data, label = station1Title[0][1])
    plt.plot(station2days, station2data, label = station2Title[0][1])
    plt.xlabel("Day")
    plt.ylabel("Number of Riders")
    plt.title("Ridership Each Day of {}".format(year))
    plt.legend()
    plt.show()


# brief: finds all stations within a square mile radius; gives the option to plot these stations on the map
# param: dbConn - database connection
# return: none
def Command9(dbConn):
    dbCursor = dbConn.cursor()

    print()

    lat = float(input("Enter a latitude: "))

    if lat < 40 or lat > 43:
        print("**Latitude entered is out of bounds...")
        return
    
    lon = float(input("Enter a longitude: "))

    if lon < -88 or lon > -87:
        print("**Longitude entered is out of bounds...")
        return
    

    minLat = round(lat - 1/69, 3)
    maxLat = round(lat + 1/69, 3)

    minLon = round(lon - 1/51, 3)
    maxLon = round(lon + 1/51, 3)

    query = """SELECT Station_Name, Latitude, Longitude FROM Stations
    JOIN Stops ON Stations.Station_ID = Stops.Station_ID
    WHERE Latitude > ? AND Latitude < ? AND Longitude > ? AND Longitude < ?
    GROUP BY Longitude, Latitude
    ORDER BY Station_Name ASC, Latitude DESC;"""

    dbCursor.execute(query, (minLat, maxLat, minLon, maxLon))
    results = dbCursor.fetchall()

    if len(results) == 0:
        print("**No stations found...\n")
        return
    
    print()
    
    print("List of Stations Within a Mile")
    for i in range(0, len(results)):
        print("{} : ({}, {})".format(results[i][0], results[i][1], results[i][2]))
    
    print()

    toPlot = input("Plot? (y/n) ")

    print()

    if toPlot != 'y':
        return

    getCoordinateQuery = """SELECT Latitude, Longitude FROM Stations
    JOIN Stops ON Stations.Station_ID = Stops.Station_ID
    WHERE Latitude > ? AND Latitude < ? AND Longitude > ? AND Longitude < ?
    GROUP BY Longitude, Latitude
    ORDER BY Station_Name ASC, Latitude DESC;"""

    dbCursor.execute(getCoordinateQuery, (minLat, maxLat, minLon, maxLon))
    coordinates = dbCursor.fetchall()

    y, x = zip(*coordinates) # to flip latitude and longitude for plotting

    image = plt.imread("chicago.png")
    xydims = [-87.9277, -87.5569, 41.7012, 42.0868]
    plt.imshow(image, extent=xydims)
    plt.title("Stations Near You")
    plt.scatter(x, y)

    for i in range(0, len(results)):
        plt.annotate(results[i][0], (x[i], y[i]))
    
    plt.xlim([-87.9277, -87.5569])
    plt.ylim([41.7012, 42.0868])
    plt.show()

    





##################################################################  
#
# main
#
print('** Welcome to CTA L analysis app **')
print()

dbConn = sqlite3.connect('CTA2_L_daily_ridership.db')

print_stats(dbConn)
print()

command = input("Please enter a command (1-9, x to exit): ")

while (command != 'x'):
    match command:
        case '1':
            Command1(dbConn)
        case '2':
            Command2(dbConn)
        case '3':
            Command3(dbConn)
        case '4':
            Command4(dbConn)
        case '5':
            Command5(dbConn)
        case '6':
            Command6(dbConn)
        case '7':
            Command7(dbConn)
        case '8':
            Command8(dbConn)
        case '9':
            Command9(dbConn)
        case _:
            print("**Error, unknown command, try again...")
    
    command = input("Please enter a command (1-9, x to exit): ")



#
# done
#
