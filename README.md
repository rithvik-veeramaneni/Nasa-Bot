# NASABot 🚀

NASABot is a Discord bot built with **Python** and **`discord.py`** that interfaces with NASA's Open APIs to bring astronomical data, space imagery, and mission archives directly into Discord communities.

---

## ⚙️ How It Works

1. **User Request:** A user triggers a Discord Slash Command in a server channel (e.g., `/apod` or `/mars-rover`).
2. **API Request:** The bot sends an HTTP request to the corresponding [NASA Open API](https://api.nasa.gov/) or the [NASA Media Library API](https://images-api.nasa.gov/).
3. **Data Processing:** The bot parses the returned JSON payload, extracts metadata (titles, descriptions, image URLs, coordinates), and formats long text to fit Discord's constraints.
4. **Discord Response:** The bot builds a formatted `discord.Embed` card featuring high-resolution images, direct media links, and interactive fields, then replies to the user.

---

## ✨ Features & Commands

* **🌌 Astronomy Picture of the Day (`/apod`)**
  * Fetches NASA's featured daily universe image or video.
  * Displays title, detailed explanation, and high-resolution download links.

* **🔴 Mars Rover Photography (`/mars-rover`)**
  * Pulls real photos taken on Mars by the **Curiosity** or **Perseverance** rovers.
  * Allows users to select which rover to view using slash command choices.
  * Displays the specific camera name, Martian Sol, and Earth date.

* **☄️ Near-Earth Object Tracker (`/neo`)**
  * Tracks asteroids passing close to Earth on the current day.
  * Shows miss distance (in km), relative speed (in km/h), and potential hazard warnings.

* **🔎 NASA Media Search (`/nasa-search [query]`)**
  * Deep-searches thousands of historical photographs and mission archives from `images-api.nasa.gov`.
  * Returns relevant media matches complete with official titles and descriptions.


* **❓ Helper Directory (`/help`)**
  * Displays an interactive list of all available slash commands and their usages.

Have Fun!!!!