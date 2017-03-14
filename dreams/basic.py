import asyncio
import json
import os
import sys

import discord
from colour import Color
from discord.ext import commands

from utils import checks
from utils.config import load_settings


class Basic:

    def __init__(self, bot):
        self.bot = bot
        self.prefix = load_settings()['prefix']
        self.err_title = load_settings()['error_title']
        self.bot_channel = load_settings()['botchannel']
        self.colourRed = 0xff0000

    @commands.command()
    async def status(self, *status:str):
        '''Change bot status.
        Usage: status "text here"
        '''
        status = ' '.join(status)
        await self.bot.change_presence(game=discord.Game(name=status))
        with open("status.txt", "a+") as f:
            f.write(status +"\n")
        em = discord.Embed(description='Changing status to: {}'.format(status), colour=0x66FF66)
        await self.bot.say(embed=em)

    @commands.command(pass_context=True,aliases=['color'])
    async def colour(self, ctx, colour:discord.Colour):
        '''Change your colour.
        Usage: colour hex_value
        '''
        try:
            bot_channel = discord.utils.find(lambda r: r.name.startswith("botspam"), list(ctx.message.server.channels))
            r = colour.r/255
            g = colour.g/255
            b = colour.b/255
            c = Color(rgb=(r, g, b))
            if c.luminance < 0.55:
                c.luminance = 0.55
            if c.saturation > 0.80:
                c.saturation = 0.80
            colour_new = discord.Colour(int(c.hex[1:], 16))
            if colour.value != colour_new.value:
                colour = colour_new
                em = discord.Embed(description='{0} your colour has been adjusted to look better on discord. New colour: {1}'.format(ctx.message.author.mention,c.hex), colour=colour)
                await self.bot.send_message(bot_channel, embed=em)

            role = discord.utils.find(lambda r: r.name.startswith(str(ctx.message.author)), list(ctx.message.server.roles))
            em = discord.Embed(description='New color set for {0}'.format(ctx.message.author.mention), colour=colour)
            if role:
                await self.bot.edit_role(ctx.message.server,role,colour=colour)
                await self.bot.add_roles(ctx.message.author,role)
                await self.bot.send_message(bot_channel, embed=em) 
            else:
                await self.bot.create_role(ctx.message.server,name=str(ctx.message.author),colour=colour)
                await asyncio.sleep(2)
                role = discord.utils.find(lambda r: r.name.startswith(str(ctx.message.author)), list(ctx.message.server.roles))
                await self.bot.add_roles(ctx.message.author, role)
                await self.bot.say(embed=em) 
        except Exception as e:
            await self.bot.say(embed=discord.Embed(title=self.err_title, description=str(e), colour=self.colourRed))

    @commands.command()
    @checks.admin_or_perm(manage_server=True)
    async def prf(self, p):
        '''Change bot prefix.
        Usage: prf new_prefix
        '''
        new_prefix = load_settings()
        new_prefix['prefix'] = p
        self.command_prefix = p
        with open('settings.json', 'w') as f:
            f.write(json.dumps(new_prefix))
        em = discord.Embed(description='Changing prefix to: {}'.format(p), colour=0x66FF66)
        await self.bot.say(embed=em)
        os.execl(sys.executable, sys.executable, * sys.argv)

def setup(bot):
    bot.add_cog(Basic(bot))
