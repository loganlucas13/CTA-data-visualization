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

    colorSearch = input("Enter a line color (e.g. Red or Yellow): ")
    checkColorQuery = "SELECT count(*) FROM Lines WHERE Color = (?) COLLATE NOCASE;"

    dbCursor.execute(checkColorQuery, (colorSearch,))

    if dbCursor.fetchone()[0] == 0:
        print("**No such line...")
        return
    
    directionSearch = input("Enter a direction (N/S/W/E): ")
    checkDirectionQuery = """SELECT count(*) FROM Stops
    JOIN StopDetails ON Stops.Stop_ID = StopDetails.Stop_ID
    JOIN Lines ON StopDetails.Line_ID = Lines.Line_ID
    WHERE Color = (?) COLLATE NOCASE AND Direction = (?) COLLATE NOCASE;"""

    dbCursor.execute(checkDirectionQuery, (colorSearch, directionSearch,))

    if dbCursor.fetchone()[0] == 0:
        print("**That line does not run in the direction chosen...")
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
        
        print("{} : direction = {} ({})".format(results[i][0], directionSearch, handicapOutput))
    
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


def Command6(dbConn):
    dbCursor = dbConn.cursor()

    search = input("Enter a station name (wildcards _ and %): ")

    checkStationQuery = """SELECT Station_Name FROM Stations WHERE Station_Name LIKE (?);"""
    dbCursor.execute(checkStationQuery, (search,))

    stationMatch = dbCursor.fetchall()

    if len(stationMatch) == 1:
        print("Yearly Ridership at {}".format(*stationMatch[0]))
    elif len(stationMatch) > 1:
        print("**Multiple stations found...")
        return
    else:
        print("**No station found...")
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

    if toPlot != 'y':
        return
    
    years, riderCount = zip(*results) # for plotting

    plt.plot(years, riderCount)
    plt.xlabel("Year")
    plt.ylabel("Number of Riders")
    plt.title("Yearly ridership at {}".format(*stationMatch[0]))
    plt.show()
        

def Command7(dbConn):
    dbCursor = dbConn.cursor()

    search = input("Enter a station name (wildcards _ and %): ")

    checkStationQuery = """SELECT Station_Name FROM Stations WHERE Station_Name LIKE (?);"""
    dbCursor.execute(checkStationQuery, (search,))

    stationMatch = dbCursor.fetchall()

    if len(stationMatch) == 1:
        year = input("Enter a year: ")
        print("Monthly ridership at {} for {}".format(*stationMatch[0], year))
    elif len(stationMatch) > 1:
        print("**Multiple stations found...")
        return
    else:
        print("**No station found...")
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



def Command8(dbConn):
    print("Command 8") 

def Command9(dbConn):
    print("Command 9") 





##################################################################  
#
# main
#
print('** Welcome to CTA L analysis app **')
print()

dbConn = sqlite3.connect('CTA2_L_daily_ridership.db')

print_stats(dbConn)

command = input("Please enter a command (1-9, x to exit): ")
print()

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
    print()



#
# done
#
