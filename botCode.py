import GUITrue as g
import discord

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    await g.menu(client)

client.run(APIKey)

