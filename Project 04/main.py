#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""
import logging

import webapp2
from google.appengine.api import mail, app_identity
from api import MemoryApi

from models import User, Game


class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        """Send a reminder email to each User with an email and an open game.
        Called every two hours using a cron job"""
        app_id = app_identity.get_application_id()
        users = User.query(User.email is not None)
        for user in users:
            # Get the first of all ative games of the user
            game = Game.query(Game.user == user.key)\
                    .filter(not Game.finished).get()

            # If at least one open game exists
            if game is not None:
                subject = 'This is a reminder!'
                body = 'Hello {}, you have at least one active memory game!'\
                    .format(user.name)
                # This will send test emails, the arguments to send_mail are:
                # from, to, subject, body
                mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                               user.email,
                               subject,
                               body)


class UpdateAverageMovesDone(webapp2.RequestHandler):
    def post(self):
        """Update game listing announcement in memcache."""
        MemoryApi._cache_average_attempts()
        self.response.set_status(204)


app = webapp2.WSGIApplication([
    ('/crons/send_open_game_reminder', SendReminderEmail),
    ('/tasks/cache_average_attempts', UpdateAverageMovesDone),
], debug=True)
