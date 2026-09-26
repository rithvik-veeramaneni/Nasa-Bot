import os
import asyncio
import discord
import requests
from discord.ext import commands
from local_config import DISCORD_BOT_TOKEN

GUILD_ID = 788782282122854400

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")
    try:
        guild = discord.Object(id=GUILD_ID)
        bot.tree.copy_global_to(guild=guild)
        synced = await bot.tree.sync(guild=guild)
        global_commands = await bot.tree.fetch_commands()
        for command in global_commands:
            await command.delete()
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

async def fetch_json(url, params=None):
    response = await asyncio.to_thread(requests.get, url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

@bot.tree.command(name="space-pic", description="Get NASA's Astronomy Picture of the Day")
async def space_pic(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        data = await fetch_json(
            "https://api.nasa.gov/planetary/apod",
            params={"api_key": os.getenv("NASA_API_KEY", "DEMO_KEY")},
        )
        explanation = data.get("explanation", "")
        if len(explanation) > 400:
            explanation = explanation[:397] + "..."
        embed = discord.Embed(
            title=data.get("title", "NASA APOD"),
            description=explanation or "No description available.",
            color=discord.Color.blue(),
        )
        if data.get("media_type") == "image":
            embed.set_image(url=data["url"])
        if data.get("url"):
            embed.url = data["url"]
        await interaction.followup.send(embed=embed)
    except requests.HTTPError as exc:
        if exc.response is not None and exc.response.status_code == 429:
            message = "NASA's shared DEMO_KEY limit is exhausted. Set NASA_API_KEY in your shell or try again later."
        else:
            message = "Couldn't retrieve NASA's Astronomy Picture of the Day."
        await interaction.followup.send(message)
    except (requests.RequestException, ValueError, KeyError):
        await interaction.followup.send("Couldn't retrieve NASA's Astronomy Picture of the Day.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.lower() == "hi":
        await message.channel.send(f"Hi, {message.author.name}!")

    if message.content.lower() == "slime you":
        await message.channel.send(f"slime you too, {message.author.name}")
    await bot.process_commands(message)

if DISCORD_BOT_TOKEN == "":
    raise RuntimeError("Add your Discord token to local_config.py before starting the bot.")

bot.run(DISCORD_BOT_TOKEN)