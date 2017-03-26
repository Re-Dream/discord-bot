import asyncio
import discord
from discord.ext import commands

if not discord.opus.is_loaded():
    discord.opus.load_opus('opus')

class Music:

    def __init__(self, bot):
        self.bot = bot
        self.player = None
        self.voice = None
        self.media_channel = None
        self.voice_channel = None
        self.song_queue = []

    def play_next(self):
        if self.song_queue[0]:
            self.player.stop()
            self.player = self.song_queue[0]
            self.song_queue.pop(0)
            self.player.start()
            crt = self.bot.send_message(self.media_channel, embed=discord.Embed(title=":musical_note: Playing queued song:", description="{0}".format(self.player.title)))
            fut = asyncio.run_coroutine_threadsafe(crt, self.bot.loop)
            try:
                fut.result()
            except:
                pass
        else:
            self.player.stop()
            vrt = self.voice.disconnect()
            fut2 = asyncio.run_coroutine_threadsafe(vrt, self.bot.loop)
            try:
                fut2.result()
            except:
                pass

    @commands.command(pass_context=True) 
    async def play(self, ctx, *, url):
        self.media_channel = ctx.message.channel
        self.voice_channel = ctx.message.author.voice_channel
        if self.voice_channel is None:
            await self.bot.say('{0} Please join a voice channel first.'.format(ctx.message.author.mention))
            return
        if self.voice is None:
            self.voice = await self.bot.join_voice_channel(self.voice_channel)
        elif self.voice.is_connected():
            await self.voice.move_to(self.voice_channel)
        try:
            options={"default_search": "ytsearch"}
            if self.player is None or self.player.is_done():
                self.player = await self.voice.create_ytdl_player(url, ytdl_options=options, after=self.play_next)
                self.player.start()
                await self.bot.send_message(self.media_channel, embed=discord.Embed(title=":musical_note: Playing song:", description="{0}".format(self.player.title)))
            else:
                if self.player.is_playing():
                    player = await self.voice.create_ytdl_player(url, ytdl_options=options, after=self.play_next)
                    self.song_queue.append(player)
                    await self.bot.send_message(self.media_channel, embed=discord.Embed(title=":timer: Added to queue:", description="{0}".format(self.player.title)))
                    print(self.song_queue)

        except Exception as e:
            print("{0} : {1}".format(type(e).__name__,str(e)))

    @commands.command(pass_context=True) 
    async def stop(self, message_object):
        if self.player is not None:
            self.player.stop()

        if self.voice is not None:
            await self.voice.disconnect()
            
def setup(bot):
    bot.add_cog(Music(bot))
