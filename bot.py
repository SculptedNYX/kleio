# Kleio Discord Bot
# Copyright (C) 2019-2022 Pim Nelissen
# Licensed under the MIT license.

# Importing all neccessary libs.
import discord, os, datetime, traceback, random, TenGiphPy
from config import *

from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, MissingPermissions
from re import search

import json_parser

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix = '!k', intents=intents)

# Loading all Python scripts inside cogs folder as cog extensions.
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')
    print(f"{filename} loaded successfully.")

# EVENTS
@client.event
async def on_ready():
    # Change the presence of the bot to state current version
    activity = discord.Activity(name=f'over the garden', type=discord.ActivityType.watching)
    await client.change_presence(activity=activity)
    print(f"[{datetime.datetime.now()}] Bot launched successfully. (Version 0.1, Discord.py version {discord.__version__}). All systems ready!")
    guild = client.get_guild(936628762144018543)
    minutely_tasks.start()
    periodic_check.start()

@client.event
async def on_member_update(old_member, new_member):

    if old_member.pending and not new_member.pending:

        animal_id = ["4Zo41lhzKt6iZ8xff9", "yjukPn2GGbMC4", "ANWIS2HYfROI8", "16StbF7VCSw6Y", "DvyLQztQwmyAM", "39xDerRCIoX2WeUVBz", "ZNegC7wFpuQT7nurZ0", "IWOEH2zDGka88", "5ceMdi7KIOYg0", "13CoXDiaCcCoyk", "8vQSQ3cNXuDGo", "5i7umUqAOYYEw", "MWSRkVoNaC30A", "Nm8ZPAGOwZUQM", "BBNYBoYa5VwtO", "Md4xQfuJeTtx6", "Dw1m8lSxkXPZC", "hzBc3HCFc0icM", "3Ev8JMnsNqUM", "DohrzSCB07moM", "SDeVLvFCqFsSA", "R8s2pWPslY0dG", "5oYgxQKHhEjEk", "1qB3EwE3c54A", "y34Ryz3lmspLq", "H6VSByAkTsrTO", "35J1lNYx6F4TOyP6tU", "P4EO3u0apt3PO", "h13NrPBRYqMOk"]

        gen_chat = new_member.guild.get_channel(GENERAL_CHAT_ID)
        welcome_squad_role = new_member.guild.get_role(WELCOME_ROLE_ID)
        current_member_count = len([m for m in new_member.guild.members if not m.bot])

        embed = discord.Embed(
            title=f"Welcome to {new_member.guild.name}, {new_member.name}!",
            description=f"The community now has `{current_member_count}` members.",
            color=0xf1c40f)

        embed.set_image(url='https://media.giphy.com/media/'+random.choice(animal_id)+'/giphy.gif')
        embed.set_author(name=new_member.name, icon_url=new_member.avatar_url)

        await gen_chat.send(f"{new_member.mention} {welcome_squad_role.mention}", embed=embed)

@client.event
async def on_command_error(ctx, error):

    if isinstance(err, commands.CommandNotFound):

        message = str(ctx.message.content)
        await embeds.Error(ctx, 10, "That command doesn't exist! Please use `.help` to see all available commands!")

    elif isinstance(err, commands.CommandOnCooldown):
        if err.retry_after >= 1800:
            time_left = f"`{round(err.retry_after/3600, 2)}` hours"
        elif err.retry_after >= 60:
            time_left = f"`{round(err.retry_after/60, 2)}` minutes"
        else:
            time_left = f"`{round(err.retry_after, 2)}` seconds"
        await embeds.Error(ctx, 10, f"Please wait {time_left} before trying again!")

    elif isinstance(err, commands.MissingPermissions) or isinstance(err, commands.CheckFailure):
        await embeds.Error(ctx, 20, f"You do not have the `{err.checks[0]}` permissions to use this command!")

    elif isinstance(err, commands.MissingRequiredArgument):
        await embeds.Error(ctx, 20, f"Missing required arguments: `{err.param}`")

    else:
        await embeds.Error(ctx, 20, f"`{ctx.command}` did not work as expected! The error was logged and a developer will take a look at it. Please try again later!")
        print(f'[{datetime.datetime.now()}] Unexpected command error: {err}')

# COMMANDS
@client.command()
@commands.check_any(commands.is_owner())
async def shutdown(ctx):
    await ctx.message.add_reaction('👍')
    print(f'[{datetime.datetime.now()}] update task cancelled.')
    periodic_check.stop()
    print(f'[{datetime.datetime.now()}] periodic task cancelled.')
    await embeds.Log("\🔌 Shutdown", ctx.guild, "`shutdown` command triggered, logging out now.")
    await client.close()

@client.command()
@commands.check_any(commands.has_permissions(administrator=True))
async def reload(ctx, extension):
    try:
        client.unload_extension(f'cogs.{extension}')
        client.load_extension(f'cogs.{extension}')
        await ctx.message.add_reaction('👍')
        await embeds.Log("\⚙️ Module Reloaded", ctx.guild, f"The `{extension}` module was reloaded successfully.")

    except:

        client.load_extension(f'cogs.{extension}')
        await ctx.message.add_reaction('👍')
        await embeds.Log("\⚙️ Module Reloaded", ctx.guild, f"The `{extension}` module was reloaded successfully.")

    print(f'[{datetime.datetime.now()}] Reloaded {extension} module.')

# TASKS
@tasks.loop(seconds=60)
async def minutely_tasks():

    guild = client.get_guild(GUILD_ID)

    # Get the member count VC channel, and update the name with the amount of people that currently have the verified member role!
    async def update_vc(client):
        member_count_vc = guild.get_channel(MEMBER_VOICE_ID)
        mem_count = len([m for m in guild.members if not m.bot])
        await member_count_vc.edit(name=f"Members: {mem_count}")

    await update_vc(client)

    try:
        channel = guild.get_channel(GENERAL_CHAT_ID)
        last_messages = await channel.history(limit=25).flatten()
        delta = datetime.datetime.utcnow() - last_messages[0].created_at
        icebreakers = await select_text('en', 'random.icebreakers')
        recently_sent = False

        for msg in last_messages:
            if msg.author.id == BOT_USER_ID:
                try: desc = msg.content
                except: desc = None

                for s in icebreakers:
                    if desc == s:
                        recently_sent = True
                        break

        if not recently_sent:
            if delta >= datetime.timedelta(seconds=90*60):
                if not last_messages[0].author.id == BOT_USER_ID:
                    await channel.send(random.choice(icebreakers))
    except:
        pass

@minutely_tasks.before_loop
async def before_minutely_tasks():
    await client.wait_until_ready()

@tasks.loop(seconds=5)
async def periodic_check():
    guild = client.get_guild(GUILD_ID)
    channel = guild.get_channel(BUMP_CHAT_ID)
    role = guild.get_role(BUMP_ROLE_ID)
    messages = await channel.history(limit=100).flatten()

    last_bot_message = None
    has_pinged = False

    for m in messages:

        if m.author.id == client.user.id and m.embeds[0].description.__contains__("It's time to bump!"):
            has_pinged = True

        if m.author.id == 302050872383242240 and m.embeds[0].description.__contains__('Bump done'):
            if datetime.datetime.utcnow() - m.created_at > datetime.timedelta(hours=2):
                last_bot_message = m
                bump_ready = True
                break
            else:
                last_bot_message = m
                bump_ready = False
                break

    if bump_ready and not has_pinged:
        embed = discord.Embed(title=None, description="🔼 It's time to bump!",colour=0x685985)
        await channel.send(role.mention,embed=embed)

client.run(json_parser.auth('discord'))
