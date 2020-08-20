import asyncio
import json
import re
from datetime import datetime
import discord
import lavalink
from discord.ext import commands
from globalcommands import GlobalCMDS as gcmds

url_rx = re.compile(r'https?://(?:www\.)?.+')

reactions = ["⏪", "⏯", "⏩", "⏹"]
plist_reactions = ["💾", "📝"]
plist_delete_reactions = ["✅", "🛑"]


class Music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.info = {}

        if not hasattr(client, 'lavalink'):
            ip = gcmds.env_check(gcmds, "LAVALINK_IP")
            port = gcmds.env_check(gcmds, "LAVALINK_PORT")
            password = gcmds.env_check(gcmds, "LAVALINK_PASSWORD")
            if not ip or not port or not password:
                pass
            else:
                client.lavalink = lavalink.Client(client.user.id)
                client.lavalink.add_node(ip, port, password, 'na', 'default-node', name="lavalink")
                client.add_listener(client.lavalink.voice_update_handler, 'on_socket_response')

        lavalink.add_event_hook(self.track_hook)
        lavalink.add_event_hook(self.update_play)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Cog "{self.qualified_name}" has been loaded')

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        player = self.client.lavalink.player_manager.get(reaction.message.guild.id)
        if reaction.emoji not in reactions:
            return
        if not user.bot and player:
            guild_id = reaction.message.guild.id
            message = self.info[str(guild_id)]['message']
            paused = self.info[str(guild_id)]['paused']
            paused_message = self.info[str(guild_id)]['paused_message']
            queue = self.info[str(guild_id)]['queue']
            rewind_message = self.info[str(guild_id)]['rewind_message']

            if message:
                if message.id == reaction.message.id:
                    await message.remove_reaction(reaction.emoji, user)
                    if reaction.emoji == "⏹":
                        if player.queue:
                            player.queue.clear()
                        await player.stop()
                        await self.del_temp_msgs(reaction.message.guild.id)
                        stopped = discord.Embed(title="Player Stopped",
                                                description=f"{user.mention}, I have stoppped the music player and "
                                                            f"cleared the queue",
                                                color=discord.Color.blue())
                        stopped.set_footer(text=f"Executed by {user.display_name} " + \
                                                "at: {:%m/%d/%Y %H:%M:%S}".format(datetime.now()))
                        await reaction.message.channel.send(embed=stopped, delete_after=5)
                    if reaction.emoji == "⏪":
                        if not queue:
                            rewind = discord.Embed(title="No Tracks to Rewind",
                                                   description=f"{user.mention}, there are no tracks to rewind to",
                                                   color=discord.Color.dark_red())
                        else:
                            index = len(queue) - len(player.queue) - 1
                            if index - 1 < 0:
                                rewind = discord.Embed(title="Rewind Failed",
                                                       description=f"{user.mention}, this is the first song in queue",
                                                       color=discord.Color.dark_red())
                                try:
                                    rewind_message_sent = await rewind_message.edit(embed=rewind, delete_after=5)
                                except (discord.NotFound, AttributeError):
                                    rewind_message_sent = await reaction.message.channel.send(embed=rewind,
                                                                                              delete_after=5)
                                await self.set_value(guild_id, 'rewind_message', rewind_message_sent)
                                return
                            track = queue[index - 1]
                            player.add(requester=user.id, track=player.current, index=0)
                            player.add(requester=user.id, track=track, index=0)
                            await player.stop()
                            await player.play()
                            rewind = discord.Embed(title="Rewind Successful",
                                                   description=f"**Now Playing:** [{track['title']}](https://www"
                                                               f".youtube.com/watch?v={track['identifier']})",
                                                   color=discord.Color.blue())
                        try:
                            rewind_message_sent = await rewind_message.edit(embed=rewind, delete_after=5)
                        except (discord.NotFound, AttributeError):
                            rewind_message_sent = await reaction.message.channel.send(embed=rewind, delete_after=5)
                        await self.set_value(guild_id, 'rewind_message', rewind_message_sent)
                    if reaction.emoji == "⏯":
                        paused = not paused
                        await player.set_pause(paused)
                        await self.set_value(guild_id, "paused", paused)
                        if paused:
                            pause = "Paused"
                        else:
                            pause = "Resumed"
                        pauseEmbed = discord.Embed(title=f"Player {pause}",
                                                   description=f"{user.mention}, the player has been {pause.lower()}",
                                                   color=discord.Color.blue())
                        pauseEmbed.set_footer(text=f"Executed by {user.display_name} " + \
                                                   "at: {:%m/%d/%Y %H:%M:%S}".format(datetime.now()))
                        try:
                            await paused_message.edit(embed=pauseEmbed, delete_after=5)
                            paused_message_sent = None
                        except (discord.NotFound, AttributeError):
                            paused_message_sent = await reaction.message.channel.send(embed=pauseEmbed)
                        await self.set_value(guild_id, "paused_message", paused_message_sent)
                    if reaction.emoji == "⏩":
                        await player.skip()
                        if not player.current:
                            skipped = discord.Embed(title="Ended Previous Track",
                                                    description=f"{user.mention}, I have finished playing all songs "
                                                                f"in queue",
                                                    color=discord.Color.blue())
                        else:
                            vid_info = f"**Now Playing:** [{player.current['title']}]" \
                                       f"(https://www.youtube.com/watch?v={player.current['identifier']}) "
                            skipped = discord.Embed(title="Skipped to Next Track",
                                                    description=f"{user.mention}, I have skipped to the next track in "
                                                                f"queue\n\n{vid_info}",
                                                    color=discord.Color.blue())
                            skipped.set_footer(text=f"Executed by {user.display_name} " + \
                                                    "at: {:%m/%d/%Y %H:%M:%S}".format(datetime.now()))
                        await reaction.message.channel.send(embed=skipped, delete_after=5)

    def cog_unload(self):
        self.client.lavalink._event_hooks.clear()
        self.info = {}

    def init_playlist(self, ctx):
        init = {f"{ctx.author.id}": {0: {'name': None, 'urls': []}}}
        gcmds.json_load(gcmds, 'playlists.json', init)

    def save_playlist(self, ctx, index: int, key: str, value):
        with open('playlists.json', 'r') as f:
            file = json.load(f)
            f.close()

        file[str(ctx.author.id)][str(index)][str(key)] = value

        with open('playlists.json', 'w') as g:
            json.dump(file, g, indent=4)

    def get_playlist(self, ctx, index: int):
        with open('playlists.json', 'r') as f:
            file = json.load(f)
            if index is not None:
                info = (file[str(ctx.author.id)][str(index)]['name'], file[str(ctx.author.id)][str(index)]['urls'])
            else:
                info = []
                incr = 0
                for _ in range(len(file[str(ctx.author.id)])):
                    info.append(
                        (file[str(ctx.author.id)][str(incr)]['name'], file[str(ctx.author.id)][str(incr)]['urls']))
                    incr += 1
            f.close()
        return info

    async def ensure_voice(self, ctx):
        player = self.client.lavalink.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
        should_connect = ctx.command.name == "play"

        if not ctx.author.voice or not ctx.author.voice.channel:
            not_conn = discord.Embed(title="Not In Voice Channel",
                                     description=f"{ctx.author.mention}, you must first join a voice channel",
                                     color=discord.Color.dark_red())
            await ctx.channel.send(embed=not_conn, delete_after=5)
            return False

        if not player.is_connected:
            if should_connect:
                permissions = ctx.author.voice.channel.permissions_for(ctx.me)
                if not permissions.connect or not permissions.speak:
                    insuf = discord.Embed(title="Insufficient Bot Permissions",
                                          description=f"{ctx.author.mention}, please make sure I have the `connect` and "
                                                      f"`speak` permissions for that voice channel",
                                          color=discord.Color.dark_red())
                    await ctx.channel.send(embed=insuf, delete_after=5)
                    return False
                player.store('channel', ctx.author.voice.channel.id)
                await self.connect_to(ctx.guild.id, str(ctx.author.voice.channel.id))
        else:
            if int(player.fetch('channel')) != ctx.author.voice.channel.id:
                diff = discord.Embed(title="Different Voice Channels",
                                     description=f"{ctx.author.mention}, make sure we're both in the same voice channel",
                                     color=discord.Color.dark_red())
                await ctx.channel.send(embed=diff, delete_after=5)
                return False

        return True

    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            guild_id = int(event.player.guild_id)
            await self.connect_to(guild_id, None)
        if isinstance(event, lavalink.events.NodeConnectedEvent):
            print(f"Connected to Lavalink Node \"{event.node.name}\"@{event.node.host}:{event.node.port}")
        if isinstance(event, lavalink.events.NodeDisconnectedEvent):
            print(f"Disconnected from Node {event.node.name} with Code {event.code} for {event.reason}")

    async def update_play(self, event):
        if isinstance(event, lavalink.events.TrackStartEvent):
            track = event.track
            ctx = self.info[str(event.player.guild_id)]['context']
            timestamp = f"Executed by {ctx.author.display_name} " + \
                        "at: {:%m/%d/%Y %H:%M:%S}".format(datetime.now())
            embed = discord.Embed(title="Now Playing",
                                  color=discord.Color.blue())
            embed.description = f'[{track["title"]}](https://www.youtube.com/watch?v={track["identifier"]})'
            embed.set_image(url=f"http://img.youtube.com/vi/{track['identifier']}/maxresdefault.jpg")
            embed.set_footer(text=timestamp)
            message = self.info[str(event.player.guild_id)]['message']
            try:
                await message.edit(embed=embed)
                message_sent = await ctx.channel.fetch_message(message.id)
            except (discord.NotFound, AttributeError):
                message_sent = await ctx.channel.send(embed=embed)
                await self.set_value(event.player.guild_id, 'message', message_sent)
            await self.add_reaction_panel(message_sent)
        if isinstance(event, lavalink.events.QueueEndEvent) or isinstance(event, lavalink.events.WebSocketClosedEvent):
            await self.del_temp_msgs(event.player.guild_id)

    async def connect_to(self, guild_id: int, channel_id: str):
        ws = self.client._connection._get_websocket(guild_id)
        await ws.voice_state(str(guild_id), channel_id)

    async def add_reaction_panel(self, message):
        for reaction in reactions:
            await message.add_reaction(reaction)

    async def no_player(self, ctx):
        invalid = discord.Embed(title="No Music Player Instance",
                                description=f"{ctx.author.mention}, I don't have a music player instance started",
                                color=discord.Color.dark_red())
        return await ctx.channel.send(embed=invalid, delete_after=5)

    async def not_owner(self, ctx):
        embed = discord.Embed(title="Not Server Owner",
                              description=f"{ctx.author.mention}, you must be the owner of this server to use this "
                                          f"command",
                              color=discord.Color.dark_red())
        await ctx.channel.send(embed=embed, delete_after=5)

    async def set_value(self, guild_id: int, key: str, value):
        try:
            self.info[str(guild_id)][key] = value
        except KeyError:
            self.info[str(guild_id)] = {'message': None, 'paused': False, 'paused_message': None, 'queue': [],
                                        'rewind_message': None, 'queue_message': None, 'volume_message': None}
            self.info[str(guild_id)][key] = value

    async def del_temp_msgs(self, guild_id: int):
        message = self.info[str(guild_id)]['message']
        paused = self.info[str(guild_id)]['paused']
        paused_message = self.info[str(guild_id)]['paused_message']
        queue = self.info[str(guild_id)]['queue']
        rewind_message = self.info[str(guild_id)]['rewind_message']
        queue_message = self.info[str(guild_id)]['queue_message']
        volume_message = self.info[str(guild_id)]['volume_message']
        if message:
            try:
                await message.delete()
            except (discord.NotFound, AttributeError, KeyError):
                pass
            await self.set_value(guild_id, 'message', None)
        if paused:
            await self.set_value(guild_id, 'paused', False)
        if paused_message:
            try:
                await paused_message.delete()
            except (discord.NotFound, AttributeError, KeyError):
                pass
            await self.set_value(guild_id, 'paused_message', None)
        if queue:
            await self.set_value(guild_id, 'queue', [])
        if rewind_message:
            try:
                await rewind_message.delete()
            except (discord.NotFound, AttributeError, KeyError):
                pass
            await self.set_value(guild_id, 'rewind_message', None)
        if queue_message:
            try:
                await queue_message.delete()
            except (discord.NotFound, AttributeError, KeyError):
                pass
            await self.set_value(guild_id, 'queue_message', None)
        if volume_message:
            try:
                await volume_message.delete()
            except (discord.NotFound, AttributeError, KeyError):
                pass
            await self.set_value(guild_id, 'volume_message', None)

    @commands.command()
    async def join(self, ctx):
        await gcmds.invkDelete(gcmds, ctx)
        player = self.client.lavalink.player_manager.get(ctx.guild.id)
        if not player:
            player = self.client.lavalink.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
        if ctx.author.voice:
            player.store("channel", ctx.author.voice.channel.id)
            if not player.is_connected:
                await self.connect_to(ctx.guild.id, ctx.author.voice.channel.id)
                joinEmbed = discord.Embed(title="Successfully Joined Voice Channel",
                                          description=f"{ctx.author.mention}, I have joined {ctx.author.voice.channel.name}",
                                          color=discord.Color.blue())
                joinEmbed.set_thumbnail(url="https://vignette.wikia.nocookie.net/mario/images/0/04/Music_Toad.jpg"
                                            "/revision/latest/top-crop/width/500/height/500?cb=20180812231020")
                joinEmbed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                await ctx.channel.send(embed=joinEmbed, delete_after=5)
                return
            elif ctx.author.voice.channel == ctx.guild.me.voice.channel:
                joinEmbed = discord.Embed(title="Already Connected to Voice Channel",
                                          description=f"{ctx.author.mention}, I'm already connected!",
                                          color=discord.Color.blue())
                joinEmbed.set_thumbnail(url="https://vignette.wikia.nocookie.net/mario/images/0/04/Music_Toad.jpg"
                                            "/revision/latest/top-crop/width/500/height/500?cb=20180812231020")
                joinEmbed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                await ctx.channel.send(embed=joinEmbed, delete_after=5)
                return
            else:
                await self.connect_to(ctx.guild.id, ctx.author.voice.channel.id)
                joinEmbed = discord.Embed(title="Successfully Moved Voice Channel",
                                          description=f"{ctx.author.mention}, I have moved to {ctx.author.voice.channel.name}",
                                          color=discord.Color.blue())
                joinEmbed.set_thumbnail(url="https://vignette.wikia.nocookie.net/mario/images/0/04/Music_Toad.jpg"
                                            "/revision/latest/top-crop/width/500/height/500?cb=20180812231020")
                joinEmbed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
                await ctx.channel.send(embed=joinEmbed, delete_after=5)
                return
        else:
            joinError = discord.Embed(title="Error",
                                      description=f"{ctx.author.mention}, please join a voice channel to use this "
                                                  f"command",
                                      color=discord.Color.dark_red())
            await ctx.channel.send(embed=joinError, delete_after=5)
            return

    @commands.command()
    async def play(self, ctx, *, query: str = None):
        await gcmds.invkDelete(gcmds, ctx)
        if not await self.ensure_voice(ctx):
            return

        await self.set_value(ctx.guild.id, "context", ctx)
        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        if ctx.author.voice:
            if not player.is_connected:
                await self.connect_to(ctx.guild.id, ctx.author.voice.channel.id)
            if not query:
                if player.queue:
                    if not player.is_playing:
                        await player.play()
                        return
                else:
                    noqueue = discord.Embed(title="Nothing in Queue",
                                            description=f"{ctx.author.mention}, please add a song to the queue to "
                                                        f"start playing",
                                            color=discord.Color.dark_red())
                    await ctx.channel.send(embed=noqueue, delete_after=15)
                    return

        query = query.strip('<>')

        if not url_rx.match(query):
            query = f'ytsearch:{query}'

        results = await player.node.get_tracks(query)

        if not results or not results['tracks']:
            notFound = discord.Embed(title="Nothing Found",
                                     description=f"{ctx.author.mention}, I couldn't find anything for *{query}*",
                                     color=discord.Color.dark_red())
            await ctx.channel.send(embed=notFound, delete_after=15)
            return

        embed = discord.Embed(color=discord.Color.blue())

        try:
            queue = self.info[str(ctx.guild.id)]['queue']
        except KeyError:
            await self.set_value(ctx.guild.id, 'queue', [])
            queue = self.info[str(ctx.guild.id)]['queue']

        # Valid loadTypes are:
        #   TRACK_LOADED    - single video/direct URL)
        #   PLAYLIST_LOADED - direct URL to playlist)
        #   SEARCH_RESULT   - query prefixed with either ytsearch: or scsearch:.
        #   NO_MATCHES      - query yielded no results
        #   LOAD_FAILED     - most likely, the video encountered an exception during loading.
        if results['loadType'] == 'PLAYLIST_LOADED':
            tracks = results['tracks']
            tracklist = []
            for track in tracks:
                tracklist.append(f"**{len(tracklist) + 1}:** [{track['info']['title']}]({track['info']['uri']})")
                player.add(requester=ctx.author.id, track=track)
                queue.append(track)

            embed.title = 'Playlist Queued!'
            embed.description = f'**[{results["playlistInfo"]["name"]}]({query})** - {len(tracks)} tracks:\n\n' + \
                                "\n".join(tracklist)
            embed.set_image(url=f"http://img.youtube.com/vi/{tracks[0]['info']['identifier']}/maxresdefault.jpg")
            embed.set_footer(text=f"Requested by: {ctx.author.display_name}")
        else:
            track = results['tracks'][0]
            embed.title = 'Track Queued'
            embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'
            embed.set_image(url=f"http://img.youtube.com/vi/{track['info']['identifier']}/maxresdefault.jpg")
            embed.set_footer(text=f"Author: {track['info']['author']}\nRequested by: {ctx.author.display_name}",
                             icon_url=ctx.author.avatar_url)

            track = lavalink.models.AudioTrack(track, ctx.author.id, recommended=True)
            player.add(requester=ctx.author.id, track=track)
            queue.append(track)

        if not player.is_playing:
            await player.play()
        else:
            queue_message = self.info[str(ctx.guild.id)]['queue_message']
            try:
                await queue_message.edit(embed=embed)
                queue_message_sent = await ctx.channel.fetch_message(queue_message.id)
            except (discord.NotFound, AttributeError):
                queue_message_sent = await ctx.channel.send(embed=embed)
            await self.set_value(ctx.guild.id, "queue_message", queue_message_sent)

        await self.set_value(ctx.guild.id, "queue", queue)

    @commands.command()
    async def queue(self, ctx, *, query: str = None):
        await gcmds.invkDelete(gcmds, ctx)
        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        if not player:
            return await self.no_player(ctx)

        if query is not None:
            if ctx.author.voice:
                if not player.is_connected:
                    notConn = discord.Embed(title="Error",
                                            description=f"{ctx.author.mention}, I must be connected to a voice "
                                                        f"channel to be able to add songs to the queue",
                                            color=discord.Color.dark_red())
                    await ctx.channel.send(embed=notConn, delete_after=15)
                    return
                else:
                    query = query.strip('<>')

                    if not url_rx.match(query):
                        query = f'ytsearch:{query}'

                    results = await player.node.get_tracks(query)

                    if not results or not results['tracks']:
                        notFound = discord.Embed(title="Nothing Found",
                                                 description=f"{ctx.author.mention}, I couldn't find anything for *{query}*",
                                                 color=discord.Color.dark_red())
                        await ctx.channel.send(embed=notFound, delete_after=15)
                        return

                    embed = discord.Embed(color=discord.Color.blue())

                    try:
                        queue = self.info[str(ctx.guild.id)]['queue']
                    except KeyError:
                        await self.set_value(ctx.guild.id, 'queue', [])
                        queue = self.info[str(ctx.guild.id)]['queue']

                    # Valid loadTypes are:
                    #   TRACK_LOADED    - single video/direct URL)
                    #   PLAYLIST_LOADED - direct URL to playlist)
                    #   SEARCH_RESULT   - query prefixed with either ytsearch: or scsearch:.
                    #   NO_MATCHES      - query yielded no results
                    #   LOAD_FAILED     - most likely, the video encountered an exception during loading.
                    if results['loadType'] == 'PLAYLIST_LOADED':
                        tracks = results['tracks']
                        tracklist = []
                        for track in tracks:
                            tracklist.append(
                                f"**{len(tracklist) + 1}:** [{track['info']['title']}]({track['info']['uri']})")
                            player.add(requester=ctx.author.id, track=track)
                            queue.append(track)

                        embed.title = 'Playlist Queued!'
                        embed.description = f'**[{results["playlistInfo"]["name"]}]({query})** - {len(tracks)} tracks' \
                                            f':\n\n' + "\n".join(tracklist)
                        embed.set_image(
                            url=f"http://img.youtube.com/vi/{tracks[0]['info']['identifier']}/maxresdefault.jpg")
                        embed.set_footer(text=f"Requested by: {ctx.author.display_name}")
                    else:
                        track = results['tracks'][0]
                        embed.title = 'Track Queued'
                        embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'
                        embed.set_image(
                            url=f"http://img.youtube.com/vi/{track['info']['identifier']}/maxresdefault.jpg")
                        embed.set_footer(
                            text=f"Author: {track['info']['author']}\nRequested by: {ctx.author.display_name}",
                            icon_url=ctx.author.avatar_url)

                        track = lavalink.models.AudioTrack(track, ctx.author.id, recommended=True)
                        player.add(requester=ctx.author.id, track=track)
                        queue.append(track)

                    message = self.info[str(ctx.guild.id)]['message']

                    if message:
                        message_sent = await message.edit(embed=embed)
                    else:
                        message_sent = await ctx.channel.send(embed=embed)
                    await self.set_value(ctx.guild.id, 'message', message_sent)
            else:
                notConn = discord.Embed(title="Error",
                                        description=f"{ctx.author.mention}, you must be connected to a voice channel "
                                                    f"to be able to add songs to the queue",
                                        color=discord.Color.dark_red())
                await ctx.channel.send(embed=notConn, delete_after=15)
                return
        else:
            if player.is_playing:
                description = [
                    f"**Now Playing:** [{player.current['title']}](https://www.youtube.com/watch?=v{player.current['identifier']})\n\n**Queue"
                    ":**\n"]
            else:
                description = []
            index = 0
            q_amt = len(player.queue)
            if q_amt == 0:
                title_append = ""
            elif q_amt == 1:
                title_append = ": 1 Track"
            else:
                title_append = f": {q_amt} Tracks"
            queueEmbed = discord.Embed(title=f"Current Queue{title_append}",
                                       color=discord.Color.blue())

            if not player.queue:
                description.append("Nothing queued")
            for item in player.queue:
                description.append(f"**{index + 1}**: [{item['title']}]"
                                   f"(https://www.youtube.com/watch?v={item['identifier']})\n")
                index += 1

            queueEmbed.description = "".join(description)

            try:
                queue_message = self.info[str(ctx.guild.id)]['queue_message']
            except KeyError:
                await self.set_value(ctx.guild.id, "queue_message", None)
                queue_message = self.info[str(ctx.guild.id)]['queue_message']

            try:
                await queue_message.edit(embed=queueEmbed)
                queue_message_sent = await ctx.channel.fetch_message(queue_message.id)
            except (discord.NotFound, AttributeError):
                queue_message_sent = await ctx.channel.send(embed=queueEmbed)
            await self.set_value(ctx.guild.id, "queue_message", queue_message_sent)

    @commands.command(aliases=['clearqueue', 'qc'])
    async def queueclear(self, ctx):
        await gcmds.invkDelete(gcmds, ctx)

        if ctx.author != ctx.guild.owner:
            return await self.not_owner(ctx)

        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        if not player:
            return await self.no_player(ctx)

        if not player.queue:
            no_queue = discord.Embed(title="Nothing in Queue",
                                     description=f"{ctx.author.mention}, there is already nothing in my queue",
                                     color=discord.Color.dark_red())
            return await ctx.channel.send(embed=no_queue, delete_after=5)

        player.queue.clear()
        await self.set_value(ctx.guild.id, 'queue', [])

        cleared = discord.Embed(title="Queue Cleared",
                                description=f"{ctx.author.mention}, I have cleared the current queue",
                                color=discord.Color.blue())
        await ctx.channel.send(embed=cleared, delete_after=5)

    @commands.command()
    async def stop(self, ctx):
        await gcmds.invkDelete(gcmds, ctx)

        if ctx.author != ctx.guild.owner:
            return await self.not_owner(ctx)

        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        if not player:
            return await self.no_player(ctx)

        if not player.is_connected:
            invalid = discord.Embed(title="Error",
                                    description=f"{ctx.author.mention}, I am not currently in a voice channel",
                                    color=discord.Color.dark_red())
            return await ctx.channel.send(embed=invalid, delete_after=5)

        if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            invalid = discord.Embed(title="Error",
                                    description=f"{ctx.author.mention}, you can only execute this command when you "
                                                f"are connected to the same voice channel as I am",
                                    color=discord.Color.dark_red())
            return await ctx.channel.send(embed=invalid, delete_after=10)
        if not player.queue and not player.is_playing:
            invalid = discord.Embed(title="Error",
                                    description=f"{ctx.author.mention}, my queue is empty",
                                    color=discord.Color.dark_red())
            return await ctx.channel.send(embed=invalid, delete_after=5)

        player.queue.clear()
        await player.stop()
        await self.del_temp_msgs(ctx.guild.id)

        stopped = discord.Embed(title="Player Stopped",
                                description=f"{ctx.author.mention}, I have stoppped the music player and cleared the "
                                            f"queue",
                                color=discord.Color.blue())
        await ctx.channel.send(embed=stopped, delete_after=5)

    @commands.command()
    async def leave(self, ctx):
        await gcmds.invkDelete(gcmds, ctx)
        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        if not player:
            return await self.no_player(ctx)

        if not player.is_connected:
            invalid = discord.Embed(title="Error",
                                    description=f"{ctx.author.mention}, I am not currently in a voice channel",
                                    color=discord.Color.dark_red())
            return await ctx.channel.send(embed=invalid, delete_after=5)

        if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            invalid = discord.Embed(title="Error",
                                    description=f"{ctx.author.mention}, you can only execute this command when you "
                                                f"are connected to the same voice channel as I am",
                                    color=discord.Color.dark_red())
            return await ctx.channel.send(embed=invalid, delete_after=10)

        player.queue.clear()
        await player.stop()
        await self.connect_to(ctx.guild.id, None)
        await self.del_temp_msgs(ctx.guild.id)
        disconnected = discord.Embed(title="Disconnected",
                                     color=discord.Color.blue())
        disconnected.set_thumbnail(url="https://i.pinimg.com/originals/56/3d/72/563d72539bbd9fccfbb427cfefdee05a"
                                       ".png")
        disconnected.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
        await ctx.channel.send(embed=disconnected, delete_after=5)

    @commands.command()
    async def volume(self, ctx, amount: int = None):
        await gcmds.invkDelete(gcmds, ctx)
        if not await self.ensure_voice(ctx):
            return
        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        if not player:
            return await self.no_player(ctx)

        if amount:
            if 1 <= amount <= 100:
                await player.set_volume(amount)
                volumeEmbed = discord.Embed(title="Current Player Volume",
                                            description=f"Current player volume set to: {player.volume}/100",
                                            color=discord.Color.blue())
            else:
                volumeEmbed = discord.Embed(title="Invalid Volume Setting",
                                            description=f"{ctx.author.mention}, the volume must be between 1 and 100",
                                            color=discord.Color.blue())
        else:
            volumeEmbed = discord.Embed(title="Current Player Volume",
                                        description=f"Current player volume set to: {player.volume}/100",
                                        color=discord.Color.blue())

        try:
            volume_message = self.info[str(ctx.guild.id)]['volume_message']
        except KeyError:
            await self.set_value(ctx.guild.id, "volume_message", None)
            volume_message = self.info[str(ctx.guild.id)]['volume_message']

        try:
            await volume_message.edit(embed=volumeEmbed)
            volume_message_sent = await ctx.channel.fetch_message(volume_message.id)
        except (discord.NotFound, AttributeError):
            volume_message_sent = await ctx.channel.send(embed=volumeEmbed)
        await self.set_value(ctx.guild.id, "volume_message", volume_message_sent)

    @commands.group(aliases=['playlists'])
    async def playlist(self, ctx):
        await gcmds.invkDelete(gcmds, ctx)
        self.init_playlist(ctx)

        name = self.get_playlist(ctx, 0)[0]
        urls = self.get_playlist(ctx, 0)[1]
        length = len(self.get_playlist(ctx, None))

        if not name and not urls and length == 1 and ctx.invoked_subcommand is None:
            no_plist = discord.Embed(title="No Playlists",
                                     description=f"{ctx.author.mention}, you have not made any playlists yet.",
                                     color=discord.Color.dark_red())
            return await ctx.channel.send(embed=no_plist, delete_after=5)

        if length != 1:
            spell = "playlists"
        else:
            spell = "playlist"

        details = self.get_playlist(ctx, None)

        index = 0

        description = f"{ctx.author.mention}, you have 💽**{length}** {spell}:\n\n"
        for name, url in details:
            index += 1
            if len(url) != 1:
                spell = "tracks"
            else:
                spell = "track"
            description += f"**{index}:** {name} ⟶ 🎶*{len(url)} {spell}*"

        playlistEmbed = discord.Embed(title=f"{ctx.author.display_name}'s Saved Playlists",
                                      description=description,
                                      color=discord.Color.blue())
        if ctx.invoked_subcommand is None:
            await ctx.channel.send(embed=playlistEmbed, delete_after=60)

    @playlist.command()
    async def load(self, ctx, *, playlist_name: str):
        await self.set_value(ctx.guild.id, 'queue', [])
        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        if not player:
            return await self.no_player(ctx)

        if not player.is_connected:
            invalid = discord.Embed(title="Error",
                                    description=f"{ctx.author.mention}, I am not currently in a voice channel",
                                    color=discord.Color.dark_red())
            return await ctx.channel.send(embed=invalid, delete_after=5)

        if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            invalid = discord.Embed(title="Error",
                                    description=f"{ctx.author.mention}, you can only execute this command when you "
                                                f"are connected to the same voice channel as I am",
                                    color=discord.Color.dark_red())
            return await ctx.channel.send(embed=invalid, delete_after=10)

        if not self.get_playlist(ctx, 0)[0]:
            no_plist = discord.Embed(title="No Playlists",
                                     description=f"{ctx.author.mention}, you have not made any playlists yet.",
                                     color=discord.Color.dark_red())
            return await ctx.channel.send(embed=no_plist, delete_after=5)

        index = 0
        exists = False

        for _ in range(len(self.get_playlist(ctx, None))):
            if playlist_name == self.get_playlist(ctx, index)[0]:
                exists = True
                break
            else:
                index += 1

        if not exists:
            no_plist = discord.Embed(title="Invalid Playlist",
                                     description=f"{ctx.author.mention}, you don't have any playlists named **{playlist_name}**",
                                     color=discord.Color.dark_red())
            return await ctx.channel.send(embed=no_plist, delete_after=10)

        for item in self.get_playlist(ctx, index)[1]:
            results = await player.node.get_tracks(item)
            track = results['tracks'][0]
            track = lavalink.models.AudioTrack(track, ctx.author.id, recommended=True)
            player.add(requester=ctx.author.id, track=track)
            self.info[str(ctx.guild.id)]['queue'].append(track)

        loaded = discord.Embed(title="Playlist Loaded",
                               description=f"{ctx.author.mention}, I have loaded all tracks to queue from **{playlist_name}**",
                               color=discord.Color.blue())
        await ctx.channel.send(embed=loaded, delete_after=10)

    @playlist.command(aliases=['edit'])
    async def save(self, ctx):
        self.init_playlist(ctx)

        try:
            queue = self.info[str(ctx.guild.id)]['queue']
        except KeyError:
            queue = None

        if not queue:
            no_queue = discord.Embed(title="No Queue Available for Saving",
                                     description=f"{ctx.author.mention}, I cannot save an empty queue as a playlist",
                                     color=discord.Color.dark_red())
            return await ctx.channel.send(embed=no_queue, delete_after=5)

        print(queue)

        urls = [f"https://www.youtube.com/watch?v={item['info']['identifier']}" for item in queue]

        panel = discord.Embed(title="Playlist Save Confirmation",
                              description=f"{ctx.author.mention}, do you want to save or edit a playlist?\n"
                                          f"React with {plist_reactions[0]} to save, or {plist_reactions[1]} to edit",
                              color=discord.Color.blue())
        panel = await ctx.channel.send(embed=panel)

        no_panel = discord.Embed(title="Playlist Setup Panel Not Found",
                                 description=f"{ctx.author.mention}, the playlist setup panel was deleted. Playlist "
                                             f"saving was cancelled",
                                 color=discord.Color.dark_red())

        for reaction in plist_reactions:
            await panel.add_reaction(reaction)

        def reaction_check(reaction, user):
            if user == ctx.author and reaction.emoji in plist_reactions and reaction.message.id == panel.id:
                return True
            else:
                return False

        def from_user(message):
            if message.author == ctx.author:
                return True
            else:
                return False

        while True:
            try:
                try:
                    panel_message = await ctx.channel.fetch_message(panel.id)
                except discord.NotFound:
                    return await ctx.channel.send(embed=no_panel, delete_after=5)
                choice = await commands.AutoShardedBot.wait_for(self.client, "reaction_add", check=reaction_check,
                                                                timeout=30)
                print(choice)
            except asyncio.TimeoutError:
                timeout = discord.Embed(title="Save Request Timed Out",
                                        description=f"{ctx.author.mention}, your save request timed out. Please try again",
                                        color=discord.Color.blue())
                return await panel.edit(embed=timeout, delete_after=10)
            else:
                if str(choice[0].emoji) == plist_reactions[0]:
                    await panel.clear_reactions()
                    action = "save"
                    break
                elif str(choice[0].emoji) == plist_reactions[1]:
                    await panel.clear_reactions()
                    action = "edit"
                    break
                else:
                    continue

        name = self.get_playlist(ctx, 0)[0]
        length = len(self.get_playlist(ctx, None))

        edit_desc = "💽**Playlists:**\n\n"
        incr = 0
        for item in self.get_playlist(ctx, None):
            incr += 1
            if len(self.get_playlist(ctx, incr - 1)[1]) != 1:
                spell = "tracks"
            else:
                spell = "track"
            edit_desc += f"**{incr}**: {item[0]} ⟶ 🎶{len(item[1])} {spell}"

        if action == "save" or not name:
            try:
                getName = discord.Embed(title="Specify the Playlist Name",
                                        description=f"{ctx.author.mention}, please specify what the playlist name should be",
                                        color=discord.Color.blue())
                await panel.edit(embed=getName)
            except discord.NotFound:
                await ctx.channel.send(embed=no_panel, delete_after=5)
            while True:
                try:
                    reply = await commands.AutoShardedBot.wait_for(self.client, "message", check=from_user, timeout=30)
                except asyncio.TimeoutError:
                    timeout = discord.Embed(title="Save Request Timed Out",
                                            description=f"{ctx.author.mention}, you did not specify a name within the "
                                                        f"time limit",
                                            color=discord.Color.blue())
                    return await panel.edit(embed=timeout, delete_after=10)
                else:
                    break

            if not name:
                index = 0
            else:
                index = length
            saveEmbed = discord.Embed(color=discord.Color.blue())
            plist_name = reply.content
            saveEmbed.title = "Saved Playlist"
            saveEmbed.description = f"Playlist Name: {plist_name}\nTracks: {len(queue)}"
            try:
                await panel.edit(embed=saveEmbed, delete_after=10)
            except discord.NotFound:
                return await ctx.channel.send(embed=no_panel, delete_after=10)
            self.save_playlist(ctx, index, "name", plist_name)
            self.save_playlist(ctx, index, "urls", urls)
            await reply.delete()
        else:
            try:
                getName = discord.Embed(title="Specify the Playlist Index",
                                        description=f"{ctx.author.mention}, type the number that is in front of the "
                                                    f"playlist you want to edit\n\n{edit_desc}",
                                        color=discord.Color.blue())
                await panel.edit(embed=getName)
            except discord.NotFound:
                return await ctx.channel.send(embed=no_panel, delete_after=5)
            while True:
                try:
                    reply = await commands.AutoShardedBot.wait_for(self.client, "message", check=from_user, timeout=30)
                except asyncio.TimeoutError:
                    timeout = discord.Embed(title="Save Request Timed Out",
                                            description=f"{ctx.author.mention}, you did not specify a name within the "
                                                        f"time limit",
                                            color=discord.Color.blue())
                    return await panel.edit(embed=timeout, delete_after=10)
                else:
                    try:
                        index = int(reply.content) - 1
                        await reply.delete()
                        break
                    except ValueError:
                        continue
            try:
                getName = discord.Embed(title="Specify the Playlist Name",
                                        description=f"{ctx.author.mention}, please specify what the playlist name "
                                                    f"should be *(enter \"skip\" to keep the playlist's current "
                                                    f"name)*\n\n**Current Name:** {self.get_playlist(ctx, index)[0]}",
                                        color=discord.Color.blue())
                await panel.edit(embed=getName)
            except discord.NotFound:
                await ctx.channel.send(embed=no_panel, delete_after=5)
            while True:
                try:
                    name_reply = await commands.AutoShardedBot.wait_for(self.client, "message", check=from_user,
                                                                        timeout=30)
                except asyncio.TimeoutError:
                    timeout = discord.Embed(title="Save Request Timed Out",
                                            description=f"{ctx.author.mention}, you did not specify a name within the "
                                                        f"time limit",
                                            color=discord.Color.blue())
                    return await panel.edit(embed=timeout, delete_after=10)
                else:
                    break
            if name_reply.content != "skip":
                self.save_playlist(ctx, index, 'name', name_reply.content)
            await name_reply.delete()
            self.save_playlist(ctx, index, "urls", urls)
            info = self.get_playlist(ctx, index)
            if len(info[1]) != 1:
                spell = "tracks"
            else:
                spell = "track"
            edited_plist = discord.Embed(title="Successfully Edited Playlist",
                                         description=f"{ctx.author.mention}, your playlist has been "
                                                     f"edited:\n\n💽**Playlist Name:** {info[0]}\n"
                                                     f"🎶**Track Count:** {len(info[1])} {spell}",
                                         color=discord.Color.blue)
            try:
                await panel.edit(embed=edited_plist, delete_after=20)
            except discord.NotFound:
                await ctx.channel.send(embed=edited_plist, delete_after=20)

    @playlist.command()
    async def add(self, ctx, playlist_id: int, *, url: str):
        return

    @playlist.command(aliases=['delete'])
    async def remove(self, ctx):
        self.init_playlist(ctx)

        def reaction_check(reaction, user):
            if user == ctx.author and reaction.emoji in plist_delete_reactions and reaction.message.id == panel.id:
                return True
            else:
                return False

        def from_user(message):
            if message.author == ctx.author:
                return True
            else:
                return False

        name = self.get_playlist(ctx, 0)[0]
        urls = self.get_playlist(ctx, 0)[1]
        length = len(self.get_playlist(ctx, None))

        if not name and not urls and length == 1:
            no_plist = discord.Embed(title="No Playlists",
                                     description=f"{ctx.author.mention}, you have not made any playlists yet.",
                                     color=discord.Color.dark_red())
            return await ctx.channel.send(embed=no_plist, delete_after=5)

        details = self.get_playlist(ctx, None)

        index = 0

        user_playlists = f"{ctx.author.mention}, type the name of the playlist you want to delete *(type \"cancel\" to cancel)*:\n\n"
        for name, url in details:
            index += 1
            if len(url) != 1:
                spell = "tracks"
            else:
                spell = "track"
            user_playlists += f"**{index}:** {name} ⟶ 🎶*{len(url)} {spell}*"

        embed = discord.Embed(title="Delete Playlist",
                              description=user_playlists,
                              color=discord.Color.blue())
        panel = await ctx.channel.send(embed=embed)

        no_panel = discord.Embed(title="Playlist Remove Panel Deleted",
                                 description=f"{ctx.author.mention}, the remove playlist panel was deleted",
                                 color=discord.Color.dark_red())

        while True:
            try:
                try:
                    panel_message = await ctx.channel.fetch_message(panel.id)
                except discord.NotFound:
                    return await ctx.channel.send(embed=no_panel, delete_after=5)
                choice = await commands.AutoShardedBot.wait_for(self.client, "message", check=from_user, timeout=30)
            except asyncio.TimeoutError:
                timeout = discord.Embed(title="Remove Request Timed Out",
                                        description=f"{ctx.author.mention}, you did not specify a name within the "
                                                    f"time limit",
                                        color=discord.Color.blue())
                return await panel.edit(embed=timeout, delete_after=10)
            else:
                if choice.content.lower() == "cancel":
                    cancelled = discord.Embed(title="Remove Request Cancelled",
                                              description=f"{ctx.author.mention}, you cancelled the remove request",
                                              color=discord.Color.blue())
                    return await panel.edit(embed=cancelled, delete_after=10)
                valid = False
                for names, urls in details:
                    if choice.content.lower() == names:
                        name = choice.content
                        valid = True
                        break
                await choice.delete()
                if valid:
                    break
                continue

        while True:
            try:
                try:
                    panel_message = await ctx.channel.fetch_message(panel.id)
                except discord.NotFound:
                    return await ctx.channel.send(embed=no_panel, delete_after=5)
                reacted = await commands.AutoShardedBot.wait_for(self.client, "reaction_add", check=reaction_check, timeout=30)
            except asyncio.TimeoutError:
                timeout = discord.Embed(title="Remove Request Timed Out",
                                        description=f"{ctx.author.mention}, you did not react within the time limit",
                                        color=discord.Color.blue())
                return await panel.edit(embed=timeout, delete_after=10)
            else:
                if str(reacted[0].emoji) == plist_delete_reactions[0]:
                    await panel.clear_reactions()
                    action = "confirm"
                    break
                elif str(reacted[0].emoji) == plist_delete_reactions[1]:
                    await panel.clear_reactions()
                    action = "cancel"
                    break
                else:
                    continue

        if action == "confirm":
            return


def setup(client):
    client.add_cog(Music(client))
