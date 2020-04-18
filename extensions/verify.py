import logging
import smtplib
import ssl
from uuid import uuid4

from discord import Color, ChannelType
from discord import Embed
from discord.ext import commands
from discord.ext.commands import Context

from bot import FS5Bot
from db import db_session
from models.user import User
from utilities import _, get_config


class Verify(commands.Cog, name="verify"):
    def __init__(self, bot: FS5Bot):
        self.bot = bot
        self.config = get_config()

    @commands.command()
    async def verify(self, ctx: Context, username: str = None):
        if ctx.channel.type != ChannelType.private:
            return await ctx.send(embed=Embed(
                color=Color.gold(),
                title=_('unsupported'),
                description=_('only supported in dm'),
            ))
        if username is None or username == '':
            return await ctx.send(embed=Embed(
                color=Color.red(),
                title=_('Errors'),
                description=_('provide username'),
            ))
        discord_id = ctx.author.id
        if User.exists(discord_id=discord_id):
            user = User.get(discord_id=discord_id)
            return await ctx.send(embed=Embed(
                color=Color.gold(),
                description=_('user already verified {mail} {username}').format(
                    mail=user.mail_address,
                    username=username,
                ),
            )) if user.verified_at is not None else await ctx.send(embed=Embed(
                color=Color.gold(),
                description=_('already sent verification {mail} {username}').format(
                    mail=user.mail_address,
                    username=username,
                ),
            ))
        await ctx.send(embed=Embed(
            color=Color.green(),
            description=_('sent verification mail {username}').format(username=username),
        ))
        mail_address = f'{username}@alumni.fh-aachen.de'
        user_id = str(uuid4())
        db_session.add(User(
            id=user_id,
            discord_id=discord_id,
            mail_address=mail_address,
        ))
        db_session.commit()
        message = f"""From: No-Reply <{self.config['verification']['mail_user']}>
To: {ctx.author.name} <{mail_address}>
Subject: Fachschaft 5 Discord Verification

Hello {ctx.author.name},

Visit this link to verify your Discord account:
    {self.config['verification']['host']}:{self.config['verification']['port']}{self.config['verification']['endpoint']}/{user_id}

Best regards
"""
        context = ssl.create_default_context()

        try:
            client = smtplib.SMTP(self.config['verification']['mail_server'], 587)
            client.ehlo()
            client.starttls(context=context)
            client.ehlo()
            client.login(self.config['verification']['mail_user'], self.config['verification']['mail_pass'])
            client.sendmail(self.config['verification']['mail_user'], [mail_address], message)
            client.quit()
        except smtplib.SMTPException as err:
            logging.error(str(err))


def setup(bot: FS5Bot):
    bot.add_cog(Verify(bot))
