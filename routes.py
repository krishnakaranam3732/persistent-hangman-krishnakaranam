from flask_restplus import Api, Resource, fields
from flask import abort, jsonify, make_response, request, url_for
from random import randint

from game import Game
from player import Player
from words import Word


def init_api_routes(app, session):
    if app:
        api = Api(app)

        words_api = api.namespace('words', description='Initialize Words (only 5 letter words allowed)')
        players_api = api.namespace('players', description='Operations on player')
        game_api = api.namespace('games', description='Operations on games')

        add_player = api.model('Player', {
                'username': fields.String})

        add_word = api.model('Word', {
                'word': fields.String})

        @words_api.route('/initialize')
        class Words(Resource):
                @words_api.response(201, 'Created')
                @words_api.response(400, 'Bad Request')
                @players_api.expect(add_word)
                def post(self):
                        '''Loads the words to database'''
                        data = request.json
                        new_word = Word(word=data["word"])

                        if len(data['word']) != 5:
                                return "Word should be exactly 5 characters long", 400

                        session.add(new_word)
                        session.commit()
                        return "Word Added successfully", 201

        @players_api.route('')
        class CreatePlayer(Resource):
                @players_api.response(200, 'Success')
                @players_api.response(400, 'Bad Request')
                @players_api.expect(add_player)
                def post(self):
                        '''Creates a player'''
                        data = request.json
                        username = data["username"]
                        already_exists = session.query(Player).filter_by(username=username).first()
                        if already_exists:
                                return "Player with username already exists", 400
                        new_player = Player(username=username)
                        session.add(new_player)
                        session.commit()
                        return session.query(Player).filter_by(username=username).first().serialize(), 200

        @players_api.route('/<int:player_id>')
        class GetPlayer(Resource):
                @players_api.response(200, 'Success')
                @players_api.response(404, 'Not Found')
                @players_api.doc(params={'player_id': 'The player_id of the ' +
                                         'player'})
                def get(self, player_id):
                        '''Gets a player'''
                        player = session.query(Player).filter_by(player_id=player_id).first()
                        if player:
                                return player.serialize(), 200
                        return "Player Does not exist", 404

        @players_api.route('/<int:player_id>/games/start')
        class CreateGame(Resource):
                @players_api.response(200, 'Success')
                @players_api.response(404, 'Not Found')
                @players_api.doc(params={'player_id': 'The player_id of the ' +
                                         'player'})
                def get(self, player_id):
                        '''Creates a game for a player'''
                        word_id = randint(1, 501)
                        correct = "_" * 5
                        guessed = ""
                        status = "new game"

                        already_exists = session.query(Player).filter_by(player_id=player_id).first()
                        if not already_exists:
                                return "Player with username doesn't exist", 400

                        new_game = Game(player_id, word_id, correct,
                                        guessed, status)
                        session.add(new_game)
                        session.commit()
                        return session.query(Game).filter_by(player_id=player_id,
                                                             word_id=word_id).first().serialize(), 200

        @players_api.route('/<int:player_id>/games')
        class AllGame(Resource):
                @players_api.response(200, 'Success')
                @players_api.doc(params={'player_id': 'The player_id of the ' +
                                         'player'})
                def get(self, player_id):
                        '''shows all games for a player'''
                        games = session.query(Game).filter_by(player_id=player_id)
                        games = [game.serialize() for game in games]
                        return games, 200

        @game_api.route('/<int:game_id>/guess/<string:guess>')
        class GuessGame(Resource):
                @game_api.response(200, 'Success')
                @game_api.response(404, 'Not Found')
                @game_api.response(400, 'Bad Request')
                @game_api.doc(params={'game_id': 'The game_id of the game',
                                      'guess': 'The guess of the game'})
                def get(self, game_id, guess):
                        '''Guesses a game for a player'''
                        game = session.query(Game).filter_by(game_id=game_id).first()
                        word = session.query(Word).filter_by(word_id=game.word_id).first().word

                        if not game:
                                return "No game with game_id exists", 404

                        if guess not in game.guessed:
                                new_guess = game.guessed + guess[0]
                        else:
                                new_guess = game.guessed
                        new_correct = game.correct
                        match = False
                        game_over = False
                        correct = ""
                        status = 400

                        for i in range(0, 5):
                                if word[i].lower() == guess.lower():
                                        correct += word[i]
                                        match = True
                                else:
                                        correct += new_correct[i]

                        if '_' not in correct:
                                game_over = True

                        game.correct = correct
                        game.guessed = new_guess

                        if game_over:
                                game.status = "Won"
                        else:
                                game.status = "progress"

                        session.add(game)
                        session.commit()
                        result = game.serialize()
                        if match:
                                status = 200
                                result['message'] = "You guessed right!"
                        else:
                                result['message'] = "You were wrong!"

                        result['guessed'] = list(game.guessed)
                        result['correct'] = list(game.correct)

                        del result['word_id']

                        return result, status

        @game_api.route('/<int:game_id>')
        class GetGame(Resource):
                @game_api.response(200, 'Success')
                @game_api.response(404, 'Not Found')
                @game_api.response(400, 'Bad Request')
                @game_api.doc(params={'game_id': 'The game_id of the game'})
                def get(self, game_id):
                        '''Guesses a game for a player'''
                        game = session.query(Game).filter_by(game_id=game_id).first()
                        return game.serialize, 200