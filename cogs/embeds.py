import discord
from discord.ext import commands

class Embeds(commands.Cog):
    
    def __init__(self, client):
        self.client = client

    # An embeded to handles errors
    async def error(self, ctx, display_time, message):
        embed = discord.Embed(title = "Error", description = message, color = 0xff2200)
        await ctx.send(embed = embed, delete_after = display_time)


def setup(client):
    client.add_cog(Embeds(client))