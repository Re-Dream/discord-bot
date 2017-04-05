import discord
from utils.config import load_settings

class Logs:

    def __init__(self, bot):
        self.bot = bot
        self.default_channel = load_settings()['defchannel']

    async def on_member_join(self, member):
        await self.bot.send_message(self.bot.get_channel(self.default_channel), "Hello {0.display_name}, welcome to {0.server.name}".format(member))

    async def on_member_remove(self, member):
        await self.bot.send_message(self.bot.get_channel(self.default_channel), "Goodbye {0.display_name}, hope you had the time of your life.".format(member))

def setup(bot):
    bot.add_cog(Logs(bot))

