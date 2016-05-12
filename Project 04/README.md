#Full Stack Nanodegree Project 4 - Memory Game

## Set-Up Instructions:
1.  Update the value of application in app.yaml to the app ID you have registered
 in the App Engine admin console and would like to use to host your instance of this sample.
1.  Run the app with the devserver using dev_appserver.py DIR, and ensure it's
 running by visiting the API Explorer - by default localhost:8080/_ah/api/explorer.
1.  (Optional) Generate your client library(ies) with the endpoints tool.
 Deploy your application.
 
 
 
##Game Description:
Guess a number is a simple guessing game. Each game begins with a random 'target'
number between the minimum and maximum values provided, and a maximum number of
'attempts'. 'Guesses' are sent to the `make_move` endpoint which will reply
with either: 'too low', 'too high', 'you win', or 'game over' (if the maximum
number of attempts is reached).
Many different Guess a Number games can be played by many different Users at any
given time. Each game can be retrieved or played by using the path parameter
`urlsafe_game_key`.

##Files Included:
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - models.py: Entity and message definitions including helper methods.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.

##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will 
    raise a ConflictException if a User with that user_name already exists.
    
 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: user_name, card_cnt (optional, default=20)
    - Returns: GameResponseForm with initial game state.
    - Description: Creates a new Game. user_name provided must correspond to an
    existing user - will raise a NotFoundException if not. card_cnt must be divisible
    by 2 and at least 4. Also adds a task to a task queue to update the average moves done
    for finished games.
     
 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameResponseForm with current game state.
    - Description: Returns the current state of a game.
    
 - **make_move**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, card_index
    - Returns: GameResponseForm with new game state.
    - Description: Accepts a 'card_index' of the card to turn around and returns
    the updated state of the game. If this causes a game to end, a corresponding 
    Score entity will be created. A valid move consists out of to make_move actions.
    To turn around the first card and the second card. If the second card turned
    around and a valid pair found, the score will be increased by 20. Otherwise
    the score will be decreased by 5. Every valid move will cause an history entry.
    If the specified card to turn around is already shown, an error message will
    be returned.
    
 - **get_scores**
    - Path: 'scores'
    - Method: GET
    - Parameters: None
    - Returns: ScoreForms
    - Description: Returns all Scores in the database (unordered).
    
 - **get_user_scores**
    - Path: 'scores/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: ScoreForms
    - Description: Returns all Scores recorded by the provided player (unordered).
    Will raise a NotFoundException if the User does not exist.
    
 - **get_average_attempts**
    - Path: 'games/average_attempts'
    - Method: GET
    - Parameters: None
    - Returns: StringMessage
    - Description: Gets the average number of attempts done for all finished
    games from a previously cached memcache key.
    
 - **get_user_games**
    - Path: 'games/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: UserGamesResponseForm. 
    - Description: Returns all of a Users's active games.
    Will raise a NotFoundException if the User does not exist.
    
 - **cancel_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: DELETE
    - Parameters: urlsafe_game_key
    - Returns: StringMessage 
    - Description: Allows users to cancel a game in progress. When canceling
    a game, it's entity will be deleted. Will raise a ForbiddenException if 
    the game already finished.
    
 - **get_high_scores**
    - Path: 'scores/leaderboard'
    - Method: GET
    - Parameters: number_of_results (optional)
    - Returns: ScoreForms
    - Description: Returns a list of high scores in descending order. The optional
    parameter 'number_of_results' limits the number of results.
    
 - **get_user_rankings**
    - Path: 'scores/userranking'
    - Method: GET
    - Parameters: None
    - Returns: UserRankingForms
    - Description: Returns each User's ranking. A User's ranking contains
    the user_name, the average score, the number of finished games, the 
    personal highscore (best_score) and the total score.
    
 - **get_game_history**
    - Path: 'game/history/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameHistoryForm
    - Description: Returns the history of moves of a game.
    E.g.: []
    
##Models Included:
 - **User**
    - Stores unique user_name, (optional) email address, the total score
    of all finished games, the number of finished games, the average score of
    all finished games and the personal highscore.
    
- **GameHistoryEntry**
    - Stores the information of a valid move. Which cards were affected and if
    a valid pair found or not.
    
 - **Game**
    - Stores unique game states. Associated with User model via KeyProperty.
    
 - **Score**
    - Records completed games. Associated with Users model via KeyProperty.
    
##Forms Included:
 - **GameResponseForm**
    - Representation of a Game's state (urlsafe_key, public_game_field,
    card_cnt, attempts_done, message, score and user_name).
 - **UserGamesResponseForm**
    - Representation of all active Game's states (urlsafe_key, public_game_field,
    card_cnt, attempts_done, message, score and user_name) of one user.
 - **NewGameForm**
    - Used to create a new game (user_name, card_cnt)
 - **MakeMoveForm**
    - Inbound make move form (card_index of card to turn around).
 - **ScoreForm**
    - Representation of a completed game's Score (user_name, date, attempts_done,
    card_cnt and score).
 - **ScoreForms**
    - Multiple ScoreForm container.
 - **UserRankingForm**
    - Representation of a user's Ranking (user_name, avg_score, finished_games,
    best_score and score).
 - **UserRankingForms**
    - Multiple UserRankingForm container.
- **GameHistoryEntryForm**
    - Representation of a valid move (card_01, card_02 and result).
 - **GameHistoryForm**
    - Multiple GameHistoryEntryForm container.
 - **StringMessage**
    - General purpose String container.