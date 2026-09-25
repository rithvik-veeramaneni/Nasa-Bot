import random
import discord
import requests
from discord import app_commands
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Could not sync commands: {e}")

@bot.command()
async def hello(ctx):
    await ctx.send("Hello!")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.lower() == "hi":
        await message.channel.send(f"Hi, {message.author.name}!")

    if message.content.lower() == "slime you":
        await message.channel.send(f"slime you too, {message.author.name}")
    await bot.process_commands(message)

bot.run("MTU1MzA5NzQxNzk3OTYwMDk0Ng.GnE6Ha.Coj2aENVEKDyOdobhPlxyPZsOb5ns4Ac0Smd-w")