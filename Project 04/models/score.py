"""score.py - This file contains the class definitions for the Datastore
entities used for score handling."""

from datetime import date
from protorpc import messages
from google.appengine.ext import ndb
from user import User


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
