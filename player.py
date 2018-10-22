from sqlalchemy import Column, String, Integer, Date, ForeignKey
from Model import Model

from pyld import jsonld


class Player(Model):
    """
        The player model
    """
    __tablename__ = 'players'

    player_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False)

    def __init__(self, username):
        self.username = username

    def __repr__(self):
        return '<player_id {}> <username {}>'.format(self.player_id,
                                                     self.username)

    def serialize(self):
        compacted_json = jsonld.compact({
            "http://schema.org/player_id": self.player_id,
            "http://schema.org/username": self.username
        }, self.get_context())
        del compacted_json['@context']
        return compacted_json

    def get_context(self):
        return {
            "@context": {
                "player_id": "http://schema.org/player_id",
                "username": "http://schema.org/username"
            }
        }