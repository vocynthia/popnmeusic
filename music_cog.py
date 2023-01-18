import discord
from discord.ext import commands

from youtube_dl import YoutubeDL


class music_cog(commands.Cog):
    __slots__ = ('bot', 'players')

    def __init__(self, bot):
        self.bot = bot
        self.players = {}
        #all the music related stuff
        self.is_playing = False

        # 2d array containing [song, channel]
        self.music_queue = []
        self.YDL_OPTIONS = {
            'format': 'bestaudio',
            'noplaylist': 'True',
            'include-ads': 'False'
        }
        self.FFMPEG_OPTIONS = {
            'before_options':
            '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }

        self.vc = ""

    #searching the item on youtube
    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" % item,
                                        download=False)['entries'][0]
            except Exception:
                return False

        return {'source': info['formats'][0]['url'], 'title': info['title']}

    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            #get the first url
            m_url = self.music_queue[0][0]['source']

            #remove the first element as you are currently playing it

            self.vc.play(
                discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS),
                after=lambda e: self.music_queue.pop(0) + self.play_next())
        else:
            self.is_playing = False

    # infinite loop checking
    async def play_music(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']

            #try to connect to voice channel if you are not already connected

            if self.vc == "" or not self.vc.is_connected() or self.vc == None:
                self.vc = await self.music_queue[0][1].connect()
            else:
                await self.vc.move_to(self.music_queue[0][1])

            print(self.music_queue)
            #remove the first element as you are currently playing it

            self.vc.play(
                discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS),
                after=lambda e: self.music_queue.pop(0) + self.play_next())

        else:
            self.is_playing = False

    #curewnt song
    @commands.command(name="now", help="Shows song that is currently playing")
    async def now_playing_(self, ctx):
        """Display information about the currently playing song."""
        title = str(self.music_queue[0][0]['title'])
        embed = discord.Embed(title="**Now Playing**",
                              description= title,
                              color=discord.Color.green())
        await ctx.send(embed=embed)

    ##play command
    @commands.command(name="play", help="Plays a selected song from youtube")
    async def p(self, ctx, *args):
        query = " ".join(args)

        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            #you need to be connected so that the bot knows where to go

            embed = discord.Embed(title="",
                                  description="Connect to a voice channel!",
                                  color=discord.Color.red())
            await ctx.send(embed=embed)
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                embed = discord.Embed(
                    title="",
                    description=
                    "Could not download the song. Incorrect format try another keyword. This could be due to playlist, livestream, or unsupported format.😭",
                    color=discord.Color.red())
                await ctx.send(embed=embed)

            else:
                embed = discord.Embed(title="",
                                      description="Song added to the queue🥺",
                                      color=discord.Color.green())
                await ctx.send(embed=embed)

                self.music_queue.append([song, voice_channel])

                if self.is_playing == False:
                    await self.play_music()

    @commands.command(name="pause", help="Pause song")
    async def pause(self, ctx, *args):
        server = ctx.message.guild
        voice_channel = server.voice_client
        voice_channel.pause()
        embed = discord.Embed(title="",
                              description="Song has paused ⏸️",
                              color=discord.Color.blue())
        await ctx.send(embed=embed)

    @commands.command(name="resume", help="Resume song")
    async def resume(self, ctx, *args):
        server = ctx.message.guild
        voice_channel = server.voice_client
        voice_channel.resume()
        embed = discord.Embed(title="",
                              description="Song has resumed ▶️",
                              color=discord.Color.blue())
        await ctx.send(embed=embed)


##show queue

    @commands.command(name="queue", help="Displays the current songs in queue")
    async def q(self, ctx):
        retval = ""
        for i in range(1, len(self.music_queue)):
            retval += self.music_queue[i][0]['title'] + "\n"

        print(retval)
        songs_num = str(len(self.music_queue) - 1)
        if retval != "":
            embed = discord.Embed(title='**' + songs_num + '**' +
                                  " **__Song(s) in Queue:__**",
                                  description= "\n" + retval,
                                  color=discord.Color.green())
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", description="Queue empty", color=discord.Color.green())
            await ctx.send(embed=embed)
##skip
    @commands.command(name="skip", help="Skips the current song being played")
    async def skip(self, ctx):
        if self.vc != "" and self.vc:
            await self.vc.stop()
            await self.music_queue.pop()
            print(self.music_queue)
            #try to play next in the queue if it exists
            self.play_next()
        else:
            self.vc.stop()
            embed = discord.Embed(title="", description="Skip error :(", color=discord.Color.red())
            await ctx.send(embed=embed)


##leave command 
    @commands.command(aliases = ["~"], help="leave channel")
    async def leave(self,ctx): 
        if (ctx.voice_client): # If the bot is in a voice channel  blue
          self.vc.stop()
     
          if len(self.music_queue) == 1 or 0 or []:
            print("none")
          else:
            self.music_queue.clear()
      
          await self.vc.disconnect() # Leave the channel
          embed = discord.Embed(title="", description="Bot Left", color=discord.Color.blue())
          await ctx.send(embed=embed)
          self.vc == ""
        else: # But if it isn't
          embed = discord.Embed(title="", description="Connect to a voice channel!", color=discord.Color.red())
          await ctx.send(embed=embed)

##clear queue
    @commands.command(name = "clear", help="clear queue")
    async def clear(self,ctx): 
        if len(self.music_queue) == 1 or 0 or []:
          embed = discord.Embed(title="", description="Queue is already empty!", color=discord.Color.red())
          await ctx.send(embed=embed)
        else:
          self.music_queue.clear()
          embed = discord.Embed(title="", description="Queue cleared", color=discord.Color.green())
          await ctx.send(embed=embed)

##leave due to inactvity
