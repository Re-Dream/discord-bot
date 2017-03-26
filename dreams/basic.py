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

    @commands.command(pass_context=True)
    async def help(self, ctx):
        '''Change bot status.
        Usage: status "text here"
        '''
        
        await self.bot.send_message(ctx.message.author,embed=discord.Embed(title="Basic Commands:",description='''```
prf       Change bot prefix.
colour    Change your colour.
status    Change bot status.```'''))
        await self.bot.send_message(ctx.message.author,embed=discord.Embed(title="Fun Commands:",description='''```
sed       Replace text in previous messages
ball8     Ask a question.
drama     Check the drama level.
wordcloud Create a word cloud
xkcd      Get random xkcd image.
yoda      Speak like yoda.
decide    Let the bot decide for you.
love      Love calculation, were you meant for each other?
urban     Check something in urban dictionary
translate Translate something.```'''))
        await self.bot.send_message(ctx.message.author,embed=discord.Embed(title="Image Processing Commands:",description='''```
wall      WE NEED TO BUILD A WALL.
blur      Blur image.
resize    Resize image.
car       Content aware resize.
avatar    Displays avatar of a given user.
caption   Caption image
edge      Enhance edges.
mtrbl     Mirror top-right to bottom-left.
meme      Make a meme
sharpen   Sharpen image.
dots      Change image into dots.
rotate    Rotate image.
mbt       Mirror bottom to top.
flop      Flip top bottom
mbrtl     Mirror bottom-right to top-left.
mrl       Mirror right to left.
flip      Flip left right
smooth    Smoothen image.
mbltr     Mirror bottom-left to top-right.
contour   Enhance contours.
e         Enlage emote.
mtlbr     Mirror top-left to bottom-right.
mlr       Mirror left to right.
grid      Change image into grid.
mtb       Mirror top to bottom.
detail    Enhance details.
lovers    They know they love each other.
emboss    Emboss contours.```'''))
        await self.bot.send_message(ctx.message.author,embed=discord.Embed(title="Music Commands:",description='''```
stop      Stops playing audio and leaves the voice channel.
play      Plays a song.```'''))
        await self.bot.send_message(ctx.message.author,embed=discord.Embed(title="NSFW Commands:",description='''```
rule34    Get random rule34 image with given tags.
danbooru  Get random danbooru image with given tags.
e621      Get random e621 image with given tags.
gelbooru  Get random gelbooru image with given tags.```'''))


    @commands.command(pass_context=True,aliases=['color'])
    async def colour(self, ctx, colour:discord.Colour):
        '''Change your colour.
        Usage: colour hex_value
        '''
        try:
            bot_channel = discord.utils.find(lambda r: r.name.startswith(self.bot_channel), list(ctx.message.server.channels))
            r = colour.r/255
            g = colour.g/255
            b = colour.b/255
            c = Color(rgb=(r, g, b))
            if c.luminance < 0.45:
                c.luminance = 0.45
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
                await self.bot.send_message(bot_channel, embed=em) 
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
