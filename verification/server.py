from configparser import ConfigParser
from datetime import datetime
from uuid import UUID

from flask import Flask

from db import db_session
from models.user import User
from utilities import _, get_config


class Server:
    def __init__(self, config: ConfigParser, app: Flask):
        self.config = config
        self.app = app

    def run(self):
        app = self.app

        @app.route('/verify/<uuid:user_id>', methods=['GET'])
        def verify(user_id: UUID):
            user = User.get(user_id=str(user_id))
            if user is None:
                return {'error': 'invalid user ID'}, 404
            user.verified_at = datetime.now()
            db_session.commit()
            return """
            <html lang="{language}">
                <head>
                    <title>Fachschaft 5 | Verified!</title>
                </head>
                <body>
                    <p style='margin: auto;'>{content}</p>
                </body>
            </html>
            """.format(language=_('language'), content=_('you can close this window now'))

        app.run(host=self.config['verification']['host'], port=self.config['verification']['port'])


if __name__ == '__main__':
    Server(get_config(), Flask(__name__)).run()
