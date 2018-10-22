from sqlalchemy import Column, String, Integer, Date, ForeignKey
from Model import Model

from pyld import jsonld


class Word(Model):
    """
        The word model
    """
    __tablename__ = 'words'

    word_id = Column(Integer, primary_key=True, autoincrement=True)
    word = Column(String(6), nullable=False)

    def __init__(self, word):
        self.word = word

    def __repr__(self):
        return '<word {}>'.format(self.word)

    def serialize(self):
        compacted_json = jsonld.compact({
            "http://schema.org/word_id": self.word_id,
            "http://schema.org/word": self.word
        }, self.get_context())
        del compacted_json['@context']
        return compacted_json

    def get_context(self):
        return {
            "@context": {
                "word_id": "http://schema.org/word_id",
                "word": "http://schema.org/word"
            }
        }