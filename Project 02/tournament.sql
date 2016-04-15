-- Table definitions for the tournament project.
-- 

-- Create the database if not existing
-- and establish connection
-- 
DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;
\c tournament;
-- 
-- Then connect to the database -> psql tournament
-- and execute the following commands.

-- Table containing all the players of the tournament
-- 
CREATE TABLE players  (id SERIAL PRIMARY KEY,
                       name VARCHAR (50) NOT NULL);

-- Table containing the already played matches
-- 
CREATE TABLE matches  (id SERIAL PRIMARY KEY,
                       winner INTEGER REFERENCES players(id),
                       loser INTEGER REFERENCES players(id));
