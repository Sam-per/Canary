#!/usr/bin/python3

import discord
from discord.ext import commands
import asyncio


class Mod():
    def __init__(self, bot):
        self.bot = bot

    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        ctx = await self.bot.get_context(message)
        if ctx.command:
            return
        if isinstance(message.channel, discord.DMChannel):
            channel_to_send = self.bot.get_channel(454061583874785280)
            msg = '{} 📣 {}'.format(str(message.author), message.content)
            await channel_to_send.send(msg)

    @commands.command(aliases=['dm'])
    @commands.has_role('Discord Moderator')
    async def pm(self, ctx, user: discord.User, *, message):
        """
        PM a user on the server using marty
        """
        dest = user
        await dest.send(message)
        channel_to_forward = self.bot.get_channel(454061583874785280)
        msg = '🐦 ({}) to {}: {}'.format(ctx.author.name, dest, message)
        await channel_to_forward.send(msg)
        await ctx.message.delete()


def setup(bot):
    bot.add_cog(Mod(bot))
