from enum import Enum


class LogChannelType(Enum):
    """
    element at value[0] is the ID of the channel type, and value[1] is the description.
    """
    General = 0, "The channel where Happy Birthday and Good Morning messages will be sent.  The guild's 'General' chat"
    MessageDeletion = 1, "The channel that deleted messages will be logged to"
    InviteCreation = 2, "The channel that new invite creations will be logged to"
    # add other log types as needed
