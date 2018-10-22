from sqlalchemy import Column, String, Integer, Date, ForeignKey
from Model import Model

from pyld import jsonld


class Game(Model):
    """
        The game model
    """
    __tablename__ = 'game'

    game_id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey('players.player_id'))
    word_id = Column(Integer, ForeignKey('words.word_id'))
    correct = Column(String(10), nullable=True)
    guessed = Column(String(30), nullable=True)
    status = Column(String(10), nullable=False)

    def __init__(self, player_id, word_id, correct, guessed, status):
        self.player_id = player_id
        self.word_id = word_id
        self.correct = correct
        self.guessed = guessed
        self.status = status

    def serialize(self):
        compacted_json = jsonld.compact({
            "http://schema.org/game_id": self.game_id,
            "http://schema.org/player_id": self.player_id,
            "http://schema.org/word_id": self.word_id,
            "http://schema.org/correct": self.correct,
            "http://schema.org/guessed": self.guessed,
            "http://schema.org/status": self.status
        }, self.get_context())
        del compacted_json['@context']
        return compacted_json

    def get_context(self):
        return {
            "@context": {
                "game_id": "http://schema.org/game_id",
                "player_id": "http://schema.org/player_id",
                "word_id": "http://schema.org/word_id",
                "correct": "http://schema.org/correct",
                "guessed": "http://schema.org/guessed",
                "status": "http://schema.org/status"
            }
        }