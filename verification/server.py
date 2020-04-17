import asyncio
from configparser import ConfigParser
from datetime import datetime
from uuid import UUID

from discord import Guild, utils, Member, Client
from flask import Flask

from db import db_session
from models.user import User
from utilities import _, get_config


class Server:
    def __init__(self, config: ConfigParser, app: Flask):
        self.config = config
        self.app = app
        self.client = Client()
        self.loop = asyncio.new_event_loop()
        self.loop.run_until_complete(self.client.login(config['bot']['token'], bot=True))

    def run(self):
        app = self.app

        @app.route('/verify/<uuid:user_id>', methods=['GET'])
        def verify(user_id: UUID):
            user = User.get(user_id=str(user_id))
            if user is None:
                return {'error': 'invalid user ID'}, 404
            user.verified_at = datetime.now()
            db_session.commit()
            self.loop.run_until_complete(self.add_role(user.discord_id))
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

    async def add_role(self, discord_id: str):
        guild: Guild = await self.client.fetch_guild(int(self.config['guild']['id']))
        member: Member = await guild.fetch_member(int(discord_id))
        role = utils.get(guild.roles, id=int(self.config['guild']['student_role_id']))
        await member.add_roles(role)


if __name__ == '__main__':
    Server(get_config(), Flask(__name__)).run()
