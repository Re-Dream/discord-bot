import discord
import json
from discord.ext import commands
import os
import sys
from utils import checks
from utils.config import load_settings
from utils.config import load_redis

class Admin:

    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True)
    @checks.is_owner()
    #@checks.admin_or_perm(manage_server=True)
    async def _set(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.bot.say('Invalid command.')

    @_set.command(pass_context=True)
    async def default(self, ctx, channel_name):
        channel = discord.utils.find(lambda r: r.name.startswith(channel_name),
                                              list(ctx.message.server.channels))
        config = load_redis()
        config.hset(ctx.message.server.id, 'defchannel', channel.id)
        em = discord.Embed(description='**{0}** saved as default channel.'.format(channel.name), colour=0x66FF66)
        await self.bot.say(embed=em)
        #os.execl(sys.executable, sys.executable, * sys.argv)

    @_set.command(pass_context=True)
    async def nsfw(self, ctx, channel_name):
        channel = discord.utils.find(lambda r: r.name.startswith(channel_name),
                                              list(ctx.message.server.channels))
        config = load_redis()
        config.hset(ctx.message.server.id, 'nsfwchannel', channel.id)
        em = discord.Embed(description='**{0}** saved as NSFW channel.'.format(channel.name), colour=0x66FF66)
        await self.bot.say(embed=em)
        #os.execl(sys.executable, sys.executable, * sys.argv)

    @_set.command(pass_context=True)
    async def bots(self, ctx, channel_name):
        channel = discord.utils.find(lambda r: r.name.startswith(channel_name),
                                              list(ctx.message.server.channels))
        config = load_redis()
        config.hset(ctx.message.server.id, 'botchannel', channel.id)
        em = discord.Embed(description='**{0}** saved as bots channel.'.format(channel.name), colour=0x66FF66)
        await self.bot.say(embed=em)
        #os.execl(sys.executable, sys.executable, * sys.argv)
        
    @commands.group(pass_context=True)
    @checks.admin_or_perm(manage_server=True)
    async def _drama(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.bot.say('Invalid command.')

    @_drama.command(pass_context=True)
    async def add(self, ctx, keyword):
        config = load_redis()
        config.rpush("drama", keyword)
        em = discord.Embed(description='**{0}** added to drama keywords.'.format(keyword), colour=0x66FF66)
        await self.bot.say(embed=em)
        #os.execl(sys.executable, sys.executable, * sys.argv)

    @commands.group(pass_context=True)
    @checks.is_owner()
    #@checks.admin_or_perm(manage_server=True)
    async def __drama(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.bot.say('Invalid command.')

    @__drama.command(pass_context=True)
    async def add(self, ctx, keyword):
        config = load_redis()
        config.rpush("drama", keyword)
        em = discord.Embed(description='**{0}** added to drama keywords.'.format(keyword), colour=0x66FF66)
        await self.bot.say(embed=em)
        #os.execl(sys.executable, sys.executable, * sys.argv)
        #     
def setup(bot):
    bot.add_cog(Admin(bot))