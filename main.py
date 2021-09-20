import discord
import keep_repl_alive

from keep_repl_alive import keep_alive
from discord.ext import commands

from music_cog import music_cog


Bot = commands.Bot(command_prefix ='++')

Bot.add_cog(music_cog(Bot))

keep_alive()

Bot.run('ODg3NTExMTg2Nzg1MDU0ODAw.YUFNNA.SwU1fL8BCpJ5tvMojyab41wS5QE')
