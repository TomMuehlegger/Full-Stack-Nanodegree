"""models.py - This file contains other model definitions"""

from protorpc import messages


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)
