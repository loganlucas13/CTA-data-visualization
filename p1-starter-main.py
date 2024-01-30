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

    checkStationQuery = "SELECT count(*) FROM Stations WHERE Station_Name = (?)"
    dbCursor.execute(checkStationQuery, (search,))

    if dbCursor.fetchone()[0] == 0: # checks if a station matches the user's search
        print("**No data found...")
    else:
        query = """SELECT sum(Num_Riders) FROM Stations
        JOIN Ridership ON Stations.Station_ID = Ridership.Station_ID 
        WHERE Type_of_Day = (?) AND Station_Name = (?)"""
        
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


# brief: outputs the total ridership on weekdays for each station (with station names)
# param: dbConn - connection to database
# return: none
def Command3(dbConn):
    print("Command 3") 

def Command4(dbConn):
    print("Command 4") 

def Command5(dbConn):
    print("Command 5") 

def Command6(dbConn):
    print("Command 6") 

def Command7(dbConn):
    print("Command 7") 

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
