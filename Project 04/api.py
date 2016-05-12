# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""


import logging
import endpoints
from protorpc import remote, messages
from google.appengine.api import memcache
from google.appengine.api import taskqueue

from models import User, Game, Score, GameHistoryEntry
from models import StringMessage, NewGameForm, GameResponseForm, MakeMoveForm,\
    ScoreForms, UserGamesResponseForm, UserRankingForms, GameHistoryForm
from utils import get_by_urlsafe

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1),)
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))
GET_USER_SCORES_REQUEST = endpoints.ResourceContainer(
        user_name=messages.StringField(1),)
GET_USER_GAMES_REQUEST = endpoints.ResourceContainer(
        user_name=messages.StringField(1),)
CANCEL_GAME_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1),)
GET_HIGH_SCORE_REQUEST = endpoints.ResourceContainer(
        number_of_results=messages.IntegerField(1),)
GET_GAME_HISTORY_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1),)

MEMCACHE_MOVES_DONE = 'MOVES_DONE'

@endpoints.api(name='memory', version='v1')
class MemoryApi(remote.Service):
    """Game API"""
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                    'A User with that name already exists!')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
                request.user_name))

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameResponseForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        try:
            game = Game.new_game(user.key, request.card_cnt)
        except ValueError, err:
            raise endpoints.BadRequestException(str(err))

        # Use a task queue to update the average attempts for finishing.
        # This operation is not needed to complete the creation of a new game
        # so it is performed out of sequence.
        taskqueue.add(url='/tasks/cache_average_attempts')
        return game.to_form('Good luck playing Memory!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameResponseForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            if game.finished:
                return game.to_form('Game already finished')
            else:
                return game.to_form('Time to make a move!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameResponseForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Makes a move. Returns a game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        
        if game.finished:
            return game.to_form('Game already finished!')
        
        if game.first_index != -1 and game.second_index != -1:
            # Reset the previous move -> no pair found
            game.public_game_field[game.first_index] = 0
            game.public_game_field[game.second_index] = 0
            game.first_index = -1
            game.second_index = -1
            
        if game.public_game_field[request.card_index] != 0:
            return game.to_form('Card already turned around!')

        # First card of a move turned already around
        if game.first_index != -1:
            # Second card not turned around
            game.public_game_field[request.card_index] = game.game_field[request.card_index]
            game.attempts_done += 1
            game.second_index = request.card_index
            
            card_01 = game.first_index
            card_02 = game.second_index

            # Found a valid pair
            if game.public_game_field[game.first_index] == game.game_field[request.card_index]:
                game.first_index = -1
                game.second_index = -1
                game.score += 20
                msg = 'Card 02 turned around - Found a valid pair!'

                # If found a valid pair and no cards left -> game finished
                if 0 not in game.public_game_field:
                    # To update the score when finishing the game
                    #game.put()
                    game.finish_game()
                    msg = 'Card 02 turned around - Found pair - Game finished!'
            # Found no pair
            else:
                game.score -= 5
                msg = 'Card 02 turned around - No pair found!'

            game_history = GameHistoryEntry(card_01=card_01,
                                            card_02=card_02,
                                            result=msg
                                            )

            game.history.append(game_history)
        else:
            # Turn around the first card of a move
            game.first_index = request.card_index
            game.public_game_field[request.card_index] = game.game_field[request.card_index]
            msg = 'Card 01 turned around!'
            
        game.put()
        return game.to_form(msg)

    @endpoints.method(response_message=ScoreForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_scores(self, request):
        """Return all scores"""
        return ScoreForms(items=[score.to_form() for score in Score.query()])
    
    @endpoints.method(request_message=GET_USER_SCORES_REQUEST,
                      response_message=ScoreForms,
                      path='scores/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request):
        """Returns all of an individual User's scores"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        scores = Score.query(Score.user == user.key)
        return ScoreForms(items=[score.to_form() for score in scores])

    @endpoints.method(response_message=StringMessage,
                      path='games/average_attempts',
                      name='get_average_attempts',
                      http_method='GET')
    def get_average_attempts(self, request):
        """Get the cached average moves done of all finished games"""
        return StringMessage(message=memcache.get(MEMCACHE_MOVES_DONE) or '')
    
    @endpoints.method(request_message=GET_USER_GAMES_REQUEST,
                      response_message=UserGamesResponseForm,
                      path='games/user/{user_name}',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Return all active games of given user."""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        
        # Return only active games (not finished)
        games = Game.query(Game.user == user.key).filter(Game.finished == False)
        return UserGamesResponseForm(user_name=user.name,
                                     games=[game.to_form('') for game in games])

    @endpoints.method(request_message=CANCEL_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/{urlsafe_game_key}',
                      name='cancel_game',
                      http_method='DELETE')
    def cancel_game(self, request):
        """Cancel a game - delete the entity."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if not game.finished:
            game.key.delete()
            return StringMessage(message='Game deleted!')
        else:
            raise endpoints.ForbiddenException('Game finished - not allowed!')
    
    @endpoints.method(request_message=GET_HIGH_SCORE_REQUEST,
                      response_message=ScoreForms,
                      path='scores/leaderboard',
                      name='get_high_scores',
                      http_method='GET')
    def get_high_scores(self, request):
        """Return a specified number of the leader board"""
        # Generates a high score list with descending order
        scores = Score.query().order(-Score.score).fetch(request.number_of_results)
        return ScoreForms(items=[score.to_form() for score in scores])

    @endpoints.method(response_message=UserRankingForms,
                      path='scores/userranking',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """Return all user rankings"""
        return UserRankingForms(items=[user.to_user_rank_form() for user in User.query()])
    
    @endpoints.method(request_message=GET_GAME_HISTORY_REQUEST,
                      response_message=GameHistoryForm,
                      path='game/history/{urlsafe_game_key}',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Return the game history of a game"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return GameHistoryForm(items=[history.to_form() for history in game.history])
        else:
            raise endpoints.NotFoundException('Game not found!')

    @staticmethod
    def _cache_average_attempts():
        """Populates memcache with the average moves remaining of Games"""
        games = Game.query(Game.finished == True).fetch()
        if games:
            count = len(games)
            total_attempts_done = sum([game.attempts_done
                                        for game in games])
            average = float(total_attempts_done)/count
            memcache.set(MEMCACHE_MOVES_DONE,
                         'The average moves done for finished games is {:.2f}'.format(average))


api = endpoints.api_server([MemoryApi])
