"""user.py - This file contains the class definitions for the Datastore
entities used for user handling."""

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


class UserRankingForm(messages.Message):
    """UserRankingForm for user Score information"""
    user_name = messages.StringField(1, required=True)
    avg_score = messages.FloatField(2, required=True)
    finished_games = messages.IntegerField(3, required=True)
    best_score = messages.IntegerField(4, required=True)
    score = messages.IntegerField(5, required=True)


class UserRankingForms(messages.Message):
    """Return multiple UserRankingForm"""
    items = messages.MessageField(UserRankingForm, 1, repeated=True)
