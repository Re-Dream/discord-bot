import asyncio
import json
import re
import threading
import random

import discord
from discord.ext import commands

from utils import checks
from utils.config import load_settings

initial_extensions = [
    'dreams.basic',
    'dreams.imageprocessing',
    'dreams.nsfw',
    'dreams.fun'
]

description = "ReDream Discord Bot"
bot = commands.Bot(command_prefix=load_settings()['prefix'], description=description)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    await asyncio.sleep(3)
    while True:
        random_lines = random.choice(open("status.txt").readlines())
        await bot.change_presence(game=discord.Game(name=random_lines))
        print("Changing status to {}".format(random_lines))
        await asyncio.sleep(120)


@bot.event
async def on_command_error(e, ctx):
    try:
        title = load_settings()["error_title"]
        if isinstance(e, checks.noRole):
            await bot.send_message(ctx.message.channel, embed=discord.Embed(title=title, description='No role or permission.', colour=0xff0000))
        elif isinstance(e, checks.noPerms):
            await bot.send_message(ctx.message.channel, embed=discord.Embed(title=title, description='No permission.', colour=0xff0000))
        elif isinstance(e, checks.noOwner):
            await bot.send_message(ctx.message.channel, embed=discord.Embed(title=title, description='Owner only.', colour=0xff0000))
        elif isinstance(e, checks.noAdmin):
            await bot.send_message(ctx.message.channel, embed=discord.Embed(title=title, description='Not an Admin.', colour=0xff0000))
        elif isinstance(e, commands.MissingRequiredArgument):
            await bot.send_message(ctx.message.channel, embed=discord.Embed(title=title, description='Argument missing.', colour=0xff0000))
        elif isinstance(e, commands.BadArgument):
            await bot.send_message(ctx.message.channel, embed=discord.Embed(title=title, description='Bad argument.', colour=0xff0000))
    except Exception as e:
        print(str(e))

if __name__ == '__main__':
    token = load_settings()['token']

    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
            print("loaded {}".format(extension))
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(
                extension, type(e).__name__, e))

    loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(bot.start(token))
except KeyboardInterrupt:
    loop.run_until_complete(bot.logout())
finally:
    loop.close()
