import os
import asyncio
import random
from datetime import datetime, timezone
import discord
from discord import app_commands
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

@bot.tree.command(name="mars-rover", description="Get a photo taken by a Mars Rover")
@app_commands.choices(rover=[
    app_commands.Choice(name="Curiosity 🤖", value="curiosity"),
    app_commands.Choice(name="Perseverance 🚜", value="perseverance"),
])
async def mars_rover(interaction: discord.Interaction, rover: app_commands.Choice[str]):
    await interaction.response.defer()
    try:
        data = await fetch_json(
            f"https://api.nasa.gov/mars-photos/api/v1/rovers/{rover.value}/photos",
            params={"sol": 1000, "api_key": os.getenv("NASA_API_KEY", "DEMO_KEY")},
        )
        photos = data.get("photos", [])
        if not photos:
            await interaction.followup.send("No photos found for this query.")
            return

        photo = random.choice(photos)
        image_url = photo.get("img_src")
        if not image_url:
            await interaction.followup.send("No photos found for this query.")
            return

        camera_name = photo.get("camera", {}).get("full_name", "Unknown Camera")
        earth_date = photo.get("earth_date", "N/A")
        embed = discord.Embed(
            title=f"{rover.value.capitalize()} Rover on Mars",
            description=f"Captured by: **{camera_name}**",
            color=discord.Color.red(),
        )
        embed.set_image(url=image_url)
        embed.set_footer(text=f"Martian Sol: 1000 • Earth Date: {earth_date}")
        await interaction.followup.send(embed=embed)
    except (requests.RequestException, ValueError, TypeError, KeyError):
        await interaction.followup.send("Failed to retrieve a photo from Mars.")

@bot.tree.command(name="neo", description="Track asteroids passing close to Earth today")
async def near_earth_objects(interaction: discord.Interaction):
    await interaction.response.defer()
    today = datetime.now(timezone.utc).date().isoformat()
    try:
        data = await fetch_json(
            "https://api.nasa.gov/neo/rest/v1/feed",
            params={
                "start_date": today,
                "end_date": today,
                "api_key": os.getenv("NASA_API_KEY", "DEMO_KEY"),
            },
        )
        asteroids = data.get("near_earth_objects", {}).get(today, [])
        count = data.get("element_count", len(asteroids))
        embed = discord.Embed(
            title="Near-Earth Object Tracker",
            description=f"NASA tracked **{count} asteroids** near Earth today.",
            color=discord.Color.dark_gold(),
        )

        for asteroid in asteroids[:4]:
            approach = (asteroid.get("close_approach_data") or [{}])[0]
            miss_distance = float(approach.get("miss_distance", {}).get("kilometers", 0))
            velocity = float(approach.get("relative_velocity", {}).get("kilometers_per_hour", 0))
            hazardous = asteroid.get("is_potentially_hazardous_asteroid", False)
            embed.add_field(
                name=f"Asteroid {asteroid.get('name', 'Unknown')}",
                value=(
                    f"**Hazardous:** {'Yes' if hazardous else 'No'}\n"
                    f"**Miss Distance:** {miss_distance:,.0f} km\n"
                    f"**Speed:** {velocity:,.0f} km/h"
                ),
                inline=True,
            )

        embed.set_footer(text="Data source: NASA NeoWS API")
        await interaction.followup.send(embed=embed)
    except (requests.RequestException, ValueError, TypeError, KeyError, IndexError):
        await interaction.followup.send("Error fetching asteroid data.")

@bot.tree.command(name="nasa-search", description="Search NASA's library of space images")
async def nasa_search(interaction: discord.Interaction, query: str):
    await interaction.response.defer()
    try:
        data = await fetch_json(
            "https://images-api.nasa.gov/search",
            params={"q": query, "media_type": "image"},
        )
        items = data.get("collection", {}).get("items", [])
        if not items:
            await interaction.followup.send(f"No images found for '{query}'.")
            return

        item = items[0]
        metadata = (item.get("data") or [{}])[0]
        links = item.get("links") or []
        title = metadata.get("title", "NASA Result")
        description = metadata.get("description", "No description available.")
        description = description[:297] + "..." if len(description) > 300 else description
        image_url = links[0].get("href") if links else None

        embed = discord.Embed(
            title=f"NASA Search: {title[:230]}",
            description=description or "No description available.",
            color=discord.Color.blue(),
        )
        if image_url:
            embed.set_image(url=image_url)
        await interaction.followup.send(embed=embed)
    except (requests.RequestException, ValueError, TypeError, KeyError, IndexError):
        await interaction.followup.send("Failed to reach NASA Image Search API.")

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