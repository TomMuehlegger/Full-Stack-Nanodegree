"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    score = ndb.IntegerProperty(required=True, default=0)
    finished_games = ndb.IntegerProperty(required=True, default=0)
    avg_score = ndb.FloatProperty(required=True, default=0.0)
    best_score = ndb.IntegerProperty(required=True, default=0)

    def finished_game(self, score):
        """User finished a game - update scores"""
        if score > self.best_score:
            self.best_score = score

        self.score += score
        self.finished_games += 1
        self.avg_score = self.score / self.finished_games
        self.put()

    def to_user_rank_form(self):
        return UserRankingForm(user_name=self.name,
                               avg_score=self.avg_score,
                               finished_games=self.finished_games,
                               best_score=self.best_score,
                               score=self.score)


class GameHistoryEntry(ndb.Model):
    """History entry object"""
    card_01 = ndb.IntegerProperty(required=True)
    card_02 = ndb.IntegerProperty(required=True)
    result = ndb.StringProperty(required=True)

    def to_form(self):
        return GameHistoryEntryForm(card_01=self.card_01,
                                    card_02=self.card_02,
                                    result=self.result)


class Game(ndb.Model):
    """Game object"""
    game_field = ndb.IntegerProperty(repeated=True)
    public_game_field = ndb.IntegerProperty(repeated=True)
    attempts_done = ndb.IntegerProperty(required=True, default=0)
    card_cnt = ndb.IntegerProperty(required=True, default=20)
    finished = ndb.BooleanProperty(required=True, default=False)
    first_index = ndb.IntegerProperty(required=True, default=-1)
    second_index = ndb.IntegerProperty(required=True, default=-1)
    score = ndb.IntegerProperty(required=True, default=0)
    history = ndb.StructuredProperty(GameHistoryEntry, repeated=True)
    user = ndb.KeyProperty(required=True, kind='User')

    @classmethod
    def new_game(cls, user, card_cnt):
        """Creates and returns a new game"""
        if card_cnt < 4:
            raise ValueError('Minimum number of cards is 4!')

        if card_cnt % 2:
            raise ValueError('Number must be divisible by 2!')

        game = Game(user=user,
                    card_cnt=card_cnt)

        shuffled_list = []

        # Create a list like [1,1,2,2,3,3,...]
        for i in xrange(0, card_cnt):
            shuffled_list.append((i / 2) + 1)

        # Do a random shuffle
        random.shuffle(shuffled_list)

        # Initialize both game_field arrays with zero
        # Zero => unknown memory image
        for i in xrange(0, card_cnt):
            game.game_field.append(shuffled_list.pop())
            game.public_game_field.append(0)

        game.put()
        return game

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameResponseForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        form.public_game_field = self.public_game_field
        form.card_cnt = self.card_cnt
        form.finished = self.finished
        form.attempts_done = self.attempts_done
        form.score = self.score
        form.message = message
        return form

    def finish_game(self):
        """Finish the game - user successfully finished the game."""
        self.finished = True
        self.put()

        # Update user score
        user = self.user.get()
        user.finished_game(self.score)

        # Add the game to the score 'board'
        score = Score(user=self.user,
                      date=date.today(),
                      attempts_done=self.attempts_done,
                      card_cnt=self.card_cnt,
                      score=self.score)
        score.put()


class Score(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    attempts_done = ndb.IntegerProperty(required=True)
    card_cnt = ndb.IntegerProperty(required=True)
    score = ndb.IntegerProperty(required=True)

    def to_form(self):
        return ScoreForm(user_name=self.user.get().name,
                         date=str(self.date),
                         attempts_done=self.attempts_done,
                         card_cnt=self.card_cnt,
                         score=self.score)


class GameResponseForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    public_game_field = messages.IntegerField(2, repeated=True)
    card_cnt = messages.IntegerField(3, required=True)
    finished = messages.BooleanField(4, required=True)
    attempts_done = messages.IntegerField(5, required=True)
    message = messages.StringField(6, required=True)
    score = messages.IntegerField(7, required=True)
    user_name = messages.StringField(8, required=True)


class UserGamesResponseForm(messages.Message):
    """UserGamesForm for outbound games state information of one user"""
    user_name = messages.StringField(1, required=True)
    games = messages.MessageField(GameResponseForm, 2, repeated=True)


class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)
    card_cnt = messages.IntegerField(2, default=20)


class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    card_index = messages.IntegerField(1, required=True)


class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    attempts_done = messages.IntegerField(3, required=True)
    card_cnt = messages.IntegerField(4, required=True)
    score = messages.IntegerField(5, required=True)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)


class UserRankingForm(messages.Message):
    """UserRankingForm for user Score information"""
    user_name = messages.StringField(1, required=True)
    avg_score = messages.FloatField(2, required=True)
    finished_games = messages.IntegerField(3, required=True)
    best_score = messages.IntegerField(4, required=True)
    score = messages.IntegerField(5, required=True)


class UserRankingForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(UserRankingForm, 1, repeated=True)


class GameHistoryEntryForm(messages.Message):
    """GameHistoryEntryForm for a game history entry"""
    card_01 = messages.IntegerField(1, required=True)
    card_02 = messages.IntegerField(2, required=True)
    result = messages.StringField(3, required=True)


class GameHistoryForm(messages.Message):
    """Return the GameHistoryEntryForms"""
    items = messages.MessageField(GameHistoryEntryForm, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)
