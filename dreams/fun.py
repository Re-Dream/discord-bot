import discord
import requests
import random
import re
from discord.ext import commands

from utils import checks
from utils.config import load_settings

class Fun:

    def __init__(self, bot):
        self.bot = bot
        self.prefix = load_settings()['prefix']
        self.err_title = load_settings()['error_title']
        self.mskey = load_settings()['mskey']
        self.colourRed = 0xff0000


    @commands.command(pass_context=True, aliases=['8ball','8'])
    async def ball8(self, ctx, text: str):
        '''Ask a question.
        Usage: 8 question
        '''
        answer = requests.get("https://api.rtainc.co/twitch/8ball?format=[0]").text
        await self.bot.say("{0} {1}".format(ctx.message.author.mention, answer))

    @commands.command(pass_context=True)
    async def decide(self, ctx, *choices: str):
        '''Let the bot decide for you.
        Usage: decide one, two, etc
        '''
        choices = ' '.join(choices)
        answer = requests.get("https://api.rtainc.co/twitch/random?format=I+choose...+%5B0%5D&choices={0}".format(choices)).text
        await self.bot.say("{0} {1}".format(ctx.message.author.mention, answer))

    @commands.command(pass_context=True, aliases=['tr'])
    async def translate(self, ctx, tl, *words: str):
        '''Translate something.
        Usage: translate from-to text_to_translate
        Example: translate en-pl sandwich
        '''
        words = ' '.join(words)
        answer = requests.get("https://translate.yandex.net/api/v1.5/tr.json/translate?key=trnsl.1.1.20170315T092303Z.ece41a1716ebea56.a289d8de3dc45f8ed21e3be5b2ab96e378f684fa&text={0}&lang={1}".format(words,tl)).json()
        print(answer)
        await self.bot.say("{0} {1}".format(ctx.message.author.mention, str(answer["text"])[2:-2]))

    @commands.command(pass_context=True)
    async def love(self, ctx, fn, sn):
        '''Love calculation, were you meant for each other?
        Usage: love first_person second_person
        '''
        answer = requests.get("https://love-calculator.p.mashape.com/getPercentage?fname={0}&sname={1}".format(fn, sn),
            headers={
                "X-Mashape-Key": self.mskey,
                "Accept": "application/json"
            }
        ).json()
        print(answer)
        await self.bot.say(embed=discord.Embed(title=":heart_exclamation: Love Calculation Result",description="{0} & {1}: **{2}%**, {3}".format(answer["fname"],answer["sname"],answer["percentage"],answer["result"]),colour=self.colourRed))

    #@commands.command(pass_context=True)
    #async def yoda(self, ctx, *text: str):
    #    '''Speak like yoda.
    #    Usage: love text
    #    '''
    #    await self.bot.send_typing(ctx.message.channel)
    #    text = '+'.join(text)
    #    answer = requests.get("https://yoda.p.mashape.com/yoda?sentence={0}".format(text),
    #        headers={
    #            "X-Mashape-Key": self.mskey,
    #            "Accept": "text/plain"
    #        }
    #    ).text
    #    await self.bot.say("**Yoda-{0}**: {1}".format(ctx.message.author.name, answer))

    @commands.command(pass_context=True)
    async def xkcd(self, ctx):
        '''Get random xkcd image.
        Usage: xkcd
        '''
        try:
            response = requests.get("https://xkcd.com/info.0.json").json()
            image_number = random.randint(1, int(response["num"]))
            response = requests.get("https://xkcd.com/{0}/info.0.json".format(image_number)).json()
            image = response["img"]
            await self.bot.say("{0}".format(image))
        except Exception as e:
            await self.bot.say(embed=discord.Embed(title=self.err_title, description=str(e), colour=self.colourRed))
                
    #this is in fun because people will mostly meme with it
    @commands.command(pass_context=True,aliases=['s'])
    async def sed(self, ctx, old, new):
        '''Replace text in previous messages
        Usage: s text_to_replace new_text
        '''
        async for msg in self.bot.logs_from(ctx.message.channel, before=ctx.message, limit=20):
            if str(old) in str(msg.content):
                print(msg.content)
                await self.bot.say("{0} thinks {1} meant to say: *{2}*".format(ctx.message.author.mention, msg.author.mention, re.sub(old, new, msg.content)))
                break

def setup(bot):
    bot.add_cog(Fun(bot))