from enum import Enum


class LogChannelType(Enum):
    """
    element at value[0] is the ID of the channel type, and value[1] is the description.
    """
    General = 0, "The server's 'general chat' channel. Happy Birthday messages and Good Morning messages " \
                 "will be sent here"
    MessageDeletion = 1, "The channel that deleted messages will be logged to"
    # add other log types as needed
