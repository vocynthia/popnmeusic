import discord
import keep_repl_alive

from keep_repl_alive import keep_alive
from discord.ext import commands

from music_cog import music_cog


Bot = commands.Bot(command_prefix ='++')

Bot.add_cog(music_cog(Bot))

keep_alive()

Bot.run('token')
