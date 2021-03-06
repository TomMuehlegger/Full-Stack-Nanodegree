#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect(database_name="tournament"):
    """Connect to the PostgreSQL database.  
       Returns a database connection and it's cursor.
    """
    try:
        db = psycopg2.connect("dbname={}".format(database_name))
        cursor = db.cursor()
        return db, cursor
    except:
        print("<error message>")


def deleteMatches():
    """Remove all the match records from the database."""
    db, cursor = connect()
    
    query = """DELETE FROM matches;"""
    cursor.execute(query)
    
    db.commit()
    db.close()

    
def deletePlayers():
    """Remove all the player records from the database."""
    db, cursor = connect()
    
    query = """DELETE FROM players;"""
    cursor.execute(query)
    
    db.commit()
    db.close()

    
def countPlayers():
    """Returns the number of players currently registered."""
    db, cursor = connect()
    
    query = """SELECT COUNT(id) FROM players;"""
    cursor.execute(query)
    results = cursor.fetchall()
    
    db.close()
    return int(results[0][0])


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    db, cursor = connect()
    
    # Be aware of security issues
    query = """INSERT INTO players (name) VALUES (%s);"""
    parameter = (name,)
    cursor.execute(query, parameter)
    
    db.commit()
    db.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or 
    a player tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    db, cursor = connect()
    
    query = """ CREATE VIEW wins AS
                SELECT p.id, p.name, COUNT(m.winner) AS wins
                FROM players AS p LEFT JOIN matches AS m
                ON (m.winner = p.id)
                GROUP BY p.id;
                
                CREATE VIEW total AS
                SELECT p.id, p.name, COUNT(m.winner) AS total
                FROM players AS p LEFT JOIN matches AS m
                ON (m.winner = p.id) OR (m.loser = p.id)
                GROUP BY p.id;
    
                SELECT wins.id, wins.name, wins.wins, total.total as matches
                FROM
                wins LEFT JOIN total   
                ON wins.id = total.id
                ORDER BY wins DESC;"""

    cursor.execute(query)
    results = cursor.fetchall()
    
    db.close()
    return results


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    db, cursor = connect()
    
    query = """INSERT INTO matches (winner, loser) VALUES (%s, %s);"""
    parameter = (int(winner), int(loser))
    cursor.execute(query, parameter)
    
    db.commit()
    db.close()
 
 
def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    # get the player standings
    standings = playerStandings()

    i = 0
    pairings = []
    leftId = 0
    leftName = ''

    # iterate over all players (sorted by wins) and
    # save the left tuple in temp variables.
    # Every even cycle add the tuple to the pairings
    for standing in standings:
        if i % 2:
            newTuple = (leftId, leftName, standing[0], standing[1])
            pairings.append(newTuple)
        else:
            leftId = standing[0]
            leftName = standing[1]

        i = i+1

    return pairings
