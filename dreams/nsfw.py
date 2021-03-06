import json
import random
import discord
import requests
from discord.ext import commands
from xml.etree import ElementTree
from PIL import Image
from io import BytesIO

from utils import checks
from utils.config import load_settings
from utils.config import load_redis

class Nsfw:

    def __init__(self, bot):
        self.bot = bot
        self.prefix = load_settings()['prefix']
        self.err_title = load_settings()['error_title']
        self.colourRed = 0xff0000

    @commands.command(pass_context=True,aliases=['e6'])
    async def e621(self, ctx, *tags: str):
        '''Get random e621 image with given tags.
        Usage: e621 "tags"
        '''
        nsfw_channel_id = load_redis().hget(ctx.message.server.id, "nsfwchannel").decode('utf-8')
        try:
            tags = ' '.join(tags)
            self.bot.send_typing(self.bot.get_channel(nsfw_channel_id))
            response = requests.get(
                "https://e621.net/post/index.json?tags={0} order:random".format(tags)).json()
            random_image = random.choice(response)
            if ctx.message.channel == self.bot.get_channel(nsfw_channel_id):
                em = discord.Embed(description='**Artist:** {0} \n **Score:** {1} \n **Direct link:** {2}'.format(random_image["artist"], random_image["score"], random_image["file_url"]),
                                   colour=0x66FF66)
            else:
                em = discord.Embed(description='Here is your image {0} \n **Artist:** {1} \n **Score:** {2} \n **Direct link:** {3}'.format(ctx.message.author.mention, random_image["artist"], random_image["score"], random_image["file_url"]),
                                   colour=0x66FF66)
            em.set_image(url=random_image["file_url"])
            em.set_author(name="e621: {0}".format(tags), icon_url="http://ai-i1.infcdn.net/icons_siandroid/jpg/300/4687/4687752.jpg")
            await self.bot.send_message(self.bot.get_channel(nsfw_channel_id), embed=em)
        except Exception as e:
            await self.bot.say(embed=discord.Embed(title=self.err_title, description=str(e), colour=self.colourRed))

    @commands.command(pass_context=True,aliases=['db'])
    async def danbooru(self, ctx, *tags: str):
        '''Get random danbooru image with given tags.
        Usage: danbooru "tags"
        '''
        nsfw_channel_id = load_redis().hget(ctx.message.server.id, "nsfwchannel").decode('utf-8')        
        try:
            tags = ' '.join(tags)
            self.bot.send_typing(self.bot.get_channel(nsfw_channel_id))
            response = requests.get(
                "http://danbooru.donmai.us/post/index.json?tags={0}".format(tags)).json()
            random_image = random.choice(response)
            if ctx.message.channel == self.bot.get_channel(nsfw_channel_id):
                em = discord.Embed(description='**Score:** {0} \n **Direct link:** http://danbooru.donmai.us{1}'.format(random_image["score"], random_image["file_url"]),
                                   colour=0x66FF66)
            else:
                em = discord.Embed(description='Here is your image {0} \n **Score:** {1} \n **Direct link:** http://danbooru.donmai.us{2}'.format(ctx.message.author.mention, random_image["score"], random_image["file_url"]),
                                   colour=0x66FF66)
            em.set_image(url="http://danbooru.donmai.us{0}".format(random_image["file_url"]))
            em.set_author(name="Danbooru: {0}".format(tags), icon_url="http://ai-i1.infcdn.net/icons_siandroid/jpg/300/4687/4687752.jpg")
            await self.bot.send_message(self.bot.get_channel(nsfw_channel_id), embed=em)
        except Exception as e:
            await self.bot.say(embed=discord.Embed(title=self.err_title, description=str(e), colour=self.colourRed))

    @commands.command(pass_context=True,aliases=['r34'])
    async def rule34(self, ctx, *tags: str):
        '''Get random rule34 image with given tags.
        Usage: rule34 "tags"
        '''
        nsfw_channel_id = load_redis().hget(ctx.message.server.id, "nsfwchannel").decode('utf-8')
        try:
            tags = ' '.join(tags)
            self.bot.send_typing(self.bot.get_channel(nsfw_channel_id))
            response = requests.get(
                "http://rule34.xxx/?page=dapi&s=post&q=index&tags={0}".format(tags))
            root = ElementTree.fromstring(response.content)
            random_post_number = random.randint(1, len(root.getchildren()))
            random_post = root[random_post_number]
            img_link = random_post.attrib["file_url"]

            if ctx.message.channel == self.bot.get_channel(nsfw_channel_id):
                em = discord.Embed(description='**Score:** {0} \n **Direct link:** http:{1}'.format(random_post.attrib["score"], img_link),
                                   colour=0x66FF66)
            else:
                em = discord.Embed(description='Here is your image {0} \n **Score:** {1} \n **Direct link:** http:{2}'.format(ctx.message.author.mention, random_post.attrib["score"], img_link),
                                   colour=0x66FF66)
            em.set_image(url="http:{0}".format(img_link))
            em.set_author(name="Rule34: {0}".format(tags), icon_url="http://ai-i1.infcdn.net/icons_siandroid/jpg/300/4687/4687752.jpg")
            await self.bot.send_message(self.bot.get_channel(nsfw_channel_id), embed=em)
        except Exception as e:
            await self.bot.say(embed=discord.Embed(title=self.err_title, description=str(e), colour=self.colourRed))

    @commands.command(pass_context=True,aliases=['gb'])
    async def gelbooru(self, ctx, *tags: str):
        '''Get random gelbooru image with given tags.
        Usage: gelbooru "tags"
        '''
        nsfw_channel_id = load_redis().hget(ctx.message.server.id, "nsfwchannel").decode('utf-8')
        try:
            tags = ' '.join(tags)
            self.bot.send_typing(self.bot.get_channel(nsfw_channel_id))
            response = requests.get(
                "http://gelbooru.com/?page=dapi&s=post&q=index&tags={0}".format(tags))
            root = ElementTree.fromstring(response.content)
            random_post_number = random.randint(1, len(root.getchildren()))
            random_post = root[random_post_number]
            img_link = random_post.attrib["file_url"]

            if ctx.message.channel == self.bot.get_channel(nsfw_channel_id):
                em = discord.Embed(description='**Score:** {0} \n **Direct link:** http:{1}'.format(random_post.attrib["score"], img_link),
                                   colour=0x66FF66)
            else:
                em = discord.Embed(description='Here is your image {0} \n **Score:** {1} \n **Direct link:** http:{2}'.format(ctx.message.author.mention, random_post.attrib["score"], img_link),
                                   colour=0x66FF66)
            em.set_image(url="http:{0}".format(img_link))
            em.set_author(name="Gelbooru: {0}".format(tags), icon_url="http://ai-i1.infcdn.net/icons_siandroid/jpg/300/4687/4687752.jpg")
            await self.bot.send_message(self.bot.get_channel(nsfw_channel_id), embed=em)
        except Exception as e:
            await self.bot.say(embed=discord.Embed(title=self.err_title, description=str(e), colour=self.colourRed))

def setup(bot):
    bot.add_cog(Nsfw(bot))
