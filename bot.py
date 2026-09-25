import os
import random
import discord
import requests
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

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

@bot.tree.command(name="hello", description="Say hello")
async def slash_hello(interaction: discord.Interaction):
    await interaction.response.send_message("Hello!")

@bot.tree.command(name="ping", description="Check if the bot is online")
async def slash_ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.lower() == "hi":
        await message.channel.send(f"Hi, {message.author.name}!")

    if message.content.lower() == "slime you":
        await message.channel.send(f"slime you too, {message.author.name}")
    await bot.process_commands(message)

token = os.getenv("DISCORD_BOT_TOKEN")
if not token:
    raise RuntimeError("Set the DISCORD_BOT_TOKEN environment variable before starting the bot.")

bot.run(token)