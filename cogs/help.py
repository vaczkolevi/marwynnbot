import random
import discord
import json
from discord.ext import commands

import globalcommands
from globalcommands import GlobalCMDS as gcmds


class Help(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Cog "help" has been loaded')

    async def syntaxEmbed(self, ctx, commandName, syntaxMessage, exampleUsage=None, exampleOutput=None, aliases=None,
                          userPerms=None, botPerms=None, specialCases=None, thumbnailURL="https://www.jing.fm/clipimg"
                                                                                         "/full/71-716621_transparent"
                                                                                         "-clip-art-open-book-frame"
                                                                                         "-line-art.png",
                          delete_after=None):
        embed = discord.Embed(title=f"{commandName} Help",
                              color=discord.Color.blue())
        embed.add_field(name="Command Syntax",
                        value=f'{syntaxMessage}')
        if exampleUsage is not None:
            embed.add_field(name="Example Usage",
                            value=exampleUsage,
                            inline=False)
        if exampleOutput is not None:
            embed.add_field(name="Output",
                            value=exampleOutput,
                            inline=False)
        if aliases is not None:
            embed.add_field(name="Aliases",
                            value=aliases,
                            inline=False)
        if userPerms is not None:
            embed.add_field(name="User Permissions Required",
                            value=userPerms,
                            inline=False)
        if botPerms is not None:
            embed.add_field(name="Bot Permissions Required",
                            value=botPerms,
                            inline=False)
        if specialCases is not None:
            embed.add_field(name="Special Cases",
                            value=specialCases,
                            inline=False)
        if thumbnailURL is not None:
            embed.set_thumbnail(url=thumbnailURL)
        if delete_after is not None:
            await ctx.channel.send(embed=embed, delete_after=delete_after)
        else:
            await ctx.channel.send(embed=embed, delete_after=delete_after)

    @commands.group(aliases=['h'])
    async def help(self, ctx):
        await ctx.message.delete()
        gcmds.incrCounter(gcmds, ctx, 'help')
        if ctx.invoked_subcommand is None:
            helpEmbed = discord.Embed(title="MarwynnBot Help Menu",
                                      colour=discord.Color(0x3498db),
                                      url="https://discord.gg/fYBTdUp",
                                      description="These are all the commands I currently support! Type"
                                                  f"\n`{gcmds.prefix(gcmds, ctx)}help [command]`\nto get help on that "
                                                  "specific command")
            helpEmbed.set_image(
                url="https://cdn.discordapp.com/avatars/623317451811061763/9bb63c734178694e8779aa102cb81062.png"
                    "?size=128")
            helpEmbed.set_thumbnail(
                url="https://www.jing.fm/clipimg/full/71-716621_transparent-clip-art-open-book-frame-line-art.png")
            helpEmbed.set_author(name="MarwynnBot",
                                 url="https://discord.gg/fYBTdUp",
                                 icon_url="https://cdn.discordapp.com/avatars/623317451811061763"
                                          "/9bb63c734178694e8779aa102cb81062.png?size=128")
            helpEmbed.set_footer(text="MarwynnBot",
                                 icon_url="https://cdn.discordapp.com/avatars/623317451811061763"
                                          "/9bb63c734178694e8779aa102cb81062.png?size=128")
            helpEmbed.add_field(name="Help",
                                value="`help`")

            debugCmds = "`ping` `shard`"
            funCmds = "`8ball` `choose` `gifsearch` `imgursearch` `isabelle` `peppa` `say` `toad`"
            gamesCmds = "`balance` `gamestats` `transfer` `blackjack` `coinflip` `connectfour` `slots` `uno`"
            moderationCmds = "`chatclean` `mute` `unmute` `kick` `ban` `unban` `modsonline`"
            musicCmds = "*Under Development* `join` `leave`"
            utilityCmds = "`prefix` `setprefix` `serverstats` `timezone`"
            ownerCmds = "`blacklist` `load` `unload` `reload` `shutdown`"

            helpEmbed.add_field(name="Debug",
                                value=debugCmds,
                                inline=False)
            helpEmbed.add_field(name="Fun",
                                value=funCmds,
                                inline=False)
            helpEmbed.add_field(name="Games",
                                value=gamesCmds,
                                inline=False)
            helpEmbed.add_field(name="Moderation",
                                value=moderationCmds,
                                inline=False)
            helpEmbed.add_field(name="Music",
                                value=musicCmds,
                                inline=False)
            helpEmbed.add_field(name="Utility",
                                value=utilityCmds,
                                inline=False)
            helpEmbed.add_field(name="Owner Only",
                                value=ownerCmds,
                                inline=False)
            await ctx.send(embed=helpEmbed)

    # =================================================
    # Help
    # =================================================

    @help.command(aliases=['h', 'help'])
    async def _help(self, ctx):
        commandName = 'Command Specific'
        syntaxMessage = f"`{gcmds.prefix(gcmds, ctx)}help [commandName]`"
        exampleUsage = f"`{gcmds.prefix(gcmds, ctx)}help ping`"
        aliases = "`h`"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               exampleUsage=exampleUsage,
                               aliases=aliases)

    # =================================================
    # Debug
    # =================================================

    @help.command()
    async def ping(self, ctx):
        commandName = 'Ping'
        syntaxMessage = f"`{gcmds.prefix(gcmds, ctx)}ping`"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage)

    @help.command()
    async def shard(self, ctx):
        commandName = "Shard"
        syntaxMessage = f"`{gcmds.prefix(gcmds, ctx)}shard [optional \"count\"]`"
        specialCases = "If the optional argument is \"count\", it will display the total number of shards"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               specialCases=specialCases)

    # =================================================
    # Fun
    # =================================================

    @help.command(aliases=['8b', '8ball'])
    async def _8ball(self, ctx):
        commandName = 'Magic 8 Ball'
        syntaxMessage = f"`{gcmds.prefix(gcmds, ctx)}8ball [question]`"
        exampleUsage = f"`{gcmds.prefix(gcmds, ctx)}8ball Is this a good bot?`"
        aliases = "`8b`"
        thumbnailURL = 'https://www.horoscope.com/images-US/games/game-magic-8-ball-no-text.png'
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               exampleUsage=exampleUsage,
                               aliases=aliases,
                               thumbnailURL=thumbnailURL)

    @help.command()
    async def choose(self, ctx):
        commandName = 'Choose'
        syntaxMessage = f"`{gcmds.prefix(gcmds, ctx)}choose [strings separated by " + "\"or\"" + " ]`"
        exampleUsage = f"`{gcmds.prefix(gcmds, ctx)}choose Chocolate or Vanilla or Strawberry or Sherbet or No ice " \
                       f"cream bc I hate it?` "
        choices = ['Chocolate', 'Vanilla', 'Strawberry', 'Sherbet', 'No ice cream because I hate it']
        exampleOutput = random.choice(choices)
        specialCases = "The word \"or\" cannot be a valid choice for the bot to pick from due to it being the splitter."
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               exampleUsage=exampleUsage,
                               exampleOutput=exampleOutput,
                               specialCases=specialCases)

    @help.command(aliases=['gifsearch', 'searchgif', 'searchgifs', 'gif', 'gifs'])
    async def gifSearch(self, ctx):
        commandName = 'GifSearch'
        syntaxMessage = f"`{gcmds.prefix(gcmds, ctx)}gifsearch [optional amount] [searchTerm]`"
        exampleUsage = f"`{gcmds.prefix(gcmds, ctx)}gifsearch excited`"
        aliases = "`gif` `gifs` `searchgif` `searchgifs`"
        specialCases = "If the `[optional amount]` argument is specified, Tenor will return that amount of gifs" \
                       "\n\nIf the `tenor_api.yaml` file is not present, it will be created and contents initialised " \
                       "as:\n```yaml\napi_key: API_KEY_FROM_TENOR\n```\nGet an API Key from Tenor and replace " \
                       "`API_KEY_FROM_TENOR` with it"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               exampleUsage=exampleUsage,
                               aliases=aliases,
                               specialCases=specialCases)

    @help.command(aliases=['imgur', 'imgursearch'])
    async def imgurSearch(self, ctx):
        commandName = "ImgurSearch"
        syntaxMessage = f"`{gcmds.prefix(gcmds, ctx)}imgursearch [optional amount] [searchTerm]`"
        exampleUsage = f"{gcmds.prefix(gcmds, ctx)}imgursearch Toad"
        aliases = "`imgur`"
        specialCases = "If the `[optional amount]` argument is specified, Imgur will return that amount of images" \
                       "\n\nIf the `imgur_api.yaml` file is not present, it will be created and contents initialised " \
                       "as:\n```yaml\nClient-ID: CLIENT_ID_FROM_IMGUR\n```\nGet a client ID from Imgur and replace " \
                       "`CLIENT_ID_FROM_IMGUR` with it"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               exampleUsage=exampleUsage,
                               aliases=aliases,
                               specialCases=specialCases)

    @help.command(aliases=['isabellepic', 'isabelleemote', 'belle', 'bellepic', 'belleemote'])
    async def isabelle(self, ctx):
        commandName = "Isabelle"
        syntaxMessage = f"`{gcmds.prefix(gcmds, ctx)}isabelle [optional amount]`"
        aliases = "`isabellepic` `isabelleemote` `belle` `bellepic` `belleemote`"
        specialCases = "If the `[optional amount]` argument is specified, it will send that many images"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               aliases=aliases,
                               specialCases=specialCases)

    @help.command(aliases=['peppapic', 'ppic', 'ppig'])
    async def peppa(self, ctx):
        commandName = "Peppa"
        syntaxMessage = f"`{gcmds.prefix(gcmds, ctx)}peppa [optional amount]`"
        aliases = "`peppapic` `ppic` `ppig`"
        specialCases = "If the `[optional amount]` argument is specified, it will send that many images"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               aliases=aliases,
                               specialCases=specialCases)

    @help.command()
    async def say(self, ctx):
        commandName = 'Say'
        syntaxMessage = f"`{gcmds.prefix(gcmds, ctx)}say`"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage)

    @help.command(alises=['toadpic', 'toademote'])
    async def toad(self, ctx):
        commandName = 'Toad'
        syntaxMessage = f"`{gcmds.prefix(gcmds, ctx)}toad [optional amount]`"
        aliases = "`toadpic` `toademote`"
        specialCases = "If the `[optional amount]` argument is specified, it will send that many images"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               aliases=aliases,
                               specialCases=specialCases)

    # =================================================
    # Games
    # =================================================

    @help.command(aliases=['gamestats', 'stats'])
    async def gameStats(self, ctx):
        commandName = "GameStats"
        syntaxMessage = f"`{gcmds.prefix(gcmds, ctx)}gamestats [optional gameName] [optional user @mentions]`"
        aliases = "`stats`"
        specialCases = 'If the `[optional gameName]` argument is not specified, it will show your stats for all the ' \
                       'games you have played at least once before' \
                       "\n\nIf the `[optional user @mentions]` argument is not specified, it will default to yourself"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               aliases=aliases,
                               specialCases=specialCases)

    @help.command()
    async def transfer(self, ctx):
        commandName = "Transfer"
        syntaxMessage = f"`{gcmds.prefix(gcmds, ctx)}transfer [amount] [user @mention or multiple @mentions]`"
        specialCases = "If the `[user @mention or multiple @mentions]` arg is more than one user, it will give `[" \
                       "amount]` to each user. You must have sufficient funds for sending to all users"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               specialCases=specialCases)

    @help.command(aliases=['bj', 'Blackjack'])
    async def blackjack(self, ctx):
        commandName = "Blackjack"
        syntaxMessage = f"`{gcmds.prefix(gcmds, ctx)}blackjack [betAmount]`"
        aliases = "`bj` `Blackjack`"
        specialCases = "If `[betAmount]` is not specified, it will automatically bet 1 credit" \
                       "\n\nIf you do not have enough credits for the `[betAmount]` you will be unable to play"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               aliases=aliases,
                               specialCases=specialCases)

    @help.command(aliases=['flip', 'cf'])
    async def coinflip(self, ctx):
        commandName = "Coinflip"
        syntaxMessage = f"`{gcmds.prefix(gcmds, ctx)}coinflip [optional betAmount] [optional face]`"
        aliases = "`flip` `cf`"
        specialCases = "If not specified:\n- `[optional betAmout]` defaults to `1`\n- `[optional face]` defaults to " \
                       "`heads` "
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               aliases=aliases,
                               specialCases=specialCases)

    @help.command(aliases=['connectfour', 'c4', 'conn', 'connect'])
    async def connectFour(self, ctx):
        commandName = "ConnectFour"
        syntaxMessage = f"`{gcmds.prefix(gcmds, ctx)}connectfour [opponent @mention]`"
        aliases = "`c4` `conn` `connect`"
        specialCases = "You can win a random amount of credits (between 1 - 5), with a very small chance " \
                       "of getting a jackpot of `1000000` credits"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               aliases=aliases,
                               specialCases=specialCases)

    @help.command(aliases=['slot'])
    async def slots(self, ctx):
        commandName = "Slots"
        syntaxMessage = f"`{gcmds.prefix(gcmds, ctx)}slots [optional betAmount or keyword]`"
        aliases = "`slot`"
        specialCases = "`[betAmount]` defaults to `1 credit` if otherwise specified\n Access the payout menu by " \
                       "entering `payout`, `rates`, or any `non-integer value` as the `[keyword]` "
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               aliases=aliases,
                               specialCases=specialCases)

    @help.command()
    async def uno(self, ctx):
        commandName = "Uno"
        syntaxMessage = f"`{gcmds.prefix(gcmds, ctx)}uno [opponent(s) @mention(s)]`"
        specialCases = "You can mention up to `9` other opponents" \
                       "\n\nYou will receive a random amount of credits that scales according to the amount of turns " \
                       "it took to establish a winner\n\n" \
                       "Cancel the game by typing `cancel` when it is your turn and you can place a card"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               specialCases=specialCases)

    # =================================================
    # Moderation
    # =================================================

    @ help.command(aliases=['clear', 'clean', 'chatclear', 'cleanchat', 'clearchat', 'purge'])
    async def chatclean(self, ctx):
        commandName = "ChatClean"
        syntaxMessage = f"`{gcmds.prefix(gcmds, ctx)}chatclean [amount] [optional user @mention]`"
        aliases = "`clear` `clean` `chatclear` `cleanchat` `clearchat` `purge`"
        userPerms = "`Manage Messages`"
        botPerms = f"`{userPerms}` or `Administrator`"
        specialCases = "When clearing chat indiscriminately, you can eliminate the `[amount]` argument and only 1 " \
                       "message will be cleared.\n\nWhen an `[optional user @mention]` is specified, the `[amount]` " \
                       "must also be specified."
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               aliases=aliases,
                               userPerms=userPerms,
                               botPerms=botPerms,
                               specialCases=specialCases)

    @help.command(aliases=['silence', 'stfu', 'shut', 'shush', 'shh', 'shhh', 'shhhh', 'quiet'])
    async def mute(self, ctx):
        commandName = "Mute"
        syntaxMessage = f"`{gcmds.prefix(gcmds, ctx)}mute [user @mentions] [optional reason]`"
        aliases = "`silence` `stfu` `shut` `shush` `shh` `shhh` `shhhh` `quiet`"
        userPerms = "`Manage Roles`"
        botPerms = "Administrator"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               aliases=aliases,
                               userPerms=userPerms,
                               botPerms=botPerms)

    @help.command(aliases=['unsilence', 'unstfu', 'unshut', 'unshush', 'unshh', 'unshhh', 'unshhhh', 'unquiet'])
    async def unmute(self, ctx):
        commandName = "Unmute"
        syntaxMessage = f"`{gcmds.prefix(gcmds, ctx)}unmute [user @mentions] [optional reason]`"
        aliases = "`unsilence` `unstfu` `unshut` `unshush` `unshh` `unshhh` `unshhhh` `unquiet`"
        userPerms = "`Manage Roles`"
        botPerms = "Administrator"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               aliases=aliases,
                               userPerms=userPerms,
                               botPerms=botPerms)

    @help.command()
    async def kick(self, ctx):
        commandName = "Kick"
        syntaxMessage = f"`{gcmds.prefix(gcmds, ctx)}kick [user @mentions] [optional reason]`"
        userPerms = "`Kick Members`"
        botPerms = f"`{userPerms}` or `Administrator`"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               userPerms=userPerms,
                               botPerms=botPerms)

    @help.command()
    async def ban(self, ctx):
        commandName = "Ban"
        syntaxMessage = f"`{gcmds.prefix(gcmds, ctx)}ban [user @mentions] [optional deleteMessageDays] [optional reason]`"
        userPerms = "`Ban Members`"
        botPerms = f"`{userPerms}` or `Administrator`"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               userPerms=userPerms,
                               botPerms=botPerms)

    @help.command()
    async def unban(self, ctx):
        commandName = "Unban"
        syntaxMessage = f"`{gcmds.prefix(gcmds, ctx)}ban [user @mentions or users + discriminators] [optional reason]`"
        userPerms = "`Unban Members`"
        botPerms = f"`{userPerms}` or `Administrator`"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               userPerms=userPerms,
                               botPerms=botPerms)

    @help.command(aliases=['mod', 'mods', 'modsonline', 'mo'])
    async def modsOnline(self, ctx):
        commandName = "ModsOnline"
        syntaxMessage = f"`{gcmds.prefix(gcmds, ctx)}modsonline`"
        aliases = "`mod` `mods` `mo`"
        specialCases = "If the server does not have a moderator role with the substring `moderator` (case " \
                       "insensitive), it will not detect that the server has a moderator role" \
                       "\n\nIf the mods have their status set to `invisible`, this command will not register them as " \
                       "being online"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               aliases=aliases,
                               specialCases=specialCases)

    # =================================================
    # Music
    # =================================================

    @help.command()
    async def join(self, ctx):
        commandName = "Join"
        syntaxMessage = f"`{gcmds.prefix(gcmds, ctx)}join`"
        userPerms = "`Connect to Voice Channel`"
        botPerms = userPerms
        specialCases = "You must currently be connected to a voice channel in order to use this command"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               userPerms=userPerms,
                               botPerms=botPerms,
                               specialCases=specialCases)

    @help.command()
    async def leave(self, ctx):
        commandName = "Leave"
        syntaxMessage = f"`{gcmds.prefix(gcmds, ctx)}leave`"
        specialCases = "You must currently be connected to a voice channel in order to use this command"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               specialCases=specialCases)

    # =================================================
    # Utility
    # =================================================

    @help.command(aliases=['counters', 'used', 'usedcount'])
    async def counter(self, ctx):
        commandName = "Counter"
        syntaxMessage = f"`{gcmds.prefix(gcmds, ctx)}counter [commandName] [optional \"global\"]`"
        exampleUsage = f"{gcmds.prefix(gcmds, ctx)}counter help"
        aliases = "`counters` `used` `usedcount`"
        specialCases = 'If the `[commandName]` is not specified, it will display the count for all executed commands' \
                       "\n\nIf the `[optional \"global\"]` argument is not specified, it defaults to per server count"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               exampleUsage=exampleUsage,
                               aliases=aliases,
                               specialCases=specialCases)

    @help.command(aliases=['p', 'checkprefix', 'prefix', 'prefixes'])
    async def _prefix(self, ctx):
        commandName = "Prefix"
        syntaxMessage = f"`{gcmds.prefix(gcmds, ctx)}prefix`"
        exampleUsage = f"`{gcmds.prefix(gcmds, ctx)}prefix`"
        exampleOutput = f"`This server's prefix is: {gcmds.prefix(gcmds, ctx)}`\n\n`The global prefixes are:" \
                        f"`{self.client.user.mention} or `mb `"
        aliases = "`p` `checkprefix` `prefixes`"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               exampleUsage=exampleUsage,
                               exampleOutput=exampleOutput,
                               aliases=aliases)

    @help.command(aliases=['sp', 'setprefix'])
    async def setPrefix(self, ctx):
        commandName = "Set Prefix"
        syntaxMessage = f"`{gcmds.prefix(gcmds, ctx)}setprefix [serverprefix]`"
        exampleUsage = f"`{gcmds.prefix(gcmds, ctx)}setprefix !m`"
        exampleOutput = "`Server prefix set to: !m`"
        aliases = "`sp`"
        specialCases = f"To reset the server prefix to bot default, enter `reset` as the `[serverprefix]` argument"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               exampleUsage=exampleUsage,
                               exampleOutput=exampleOutput,
                               aliases=aliases,
                               specialCases=specialCases)

    @help.command(aliases=['ss', 'serverstats', 'serverstatistics'])
    async def serverStats(self, ctx):
        commandName = "Server Stats"
        syntaxMessage = f"`{gcmds.prefix(gcmds, ctx)}serverstats [optional \"reset\"]`"
        aliases = "`ss` `serverstatistics`"
        userPerms = '`Administrator`'
        botPerms = userPerms
        specialCases = "If the `reset` argument is present, it will delete the currently active server stats channels" \
                       " and category\n\nYou will not be able to create another server stats panel if one" \
                       " already exists"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               aliases=aliases,
                               userPerms=userPerms,
                               botPerms=botPerms,
                               specialCases=specialCases)

    @help.command(aliases=['tz'])
    async def timezone(self, ctx):
        commandName = "Timezone"
        syntaxMessage = f"`{gcmds.prefix(gcmds, ctx)}timezone [GMT time]`"
        exampleUsage = f"`{gcmds.prefix(gcmds, ctx)}timezone GMT+4`"
        exampleOutput = f"{ctx.author.mention}'s nickname will be changed to: `{ctx.author.display_name} [GMT+4]`"
        aliases = "`tz`"
        userPerms = '`Change Nickname`'
        botPerms = "`Administrator`"
        specialCases = "If the `[GMT time]` argument is `reset` or `r`, the tag will be removed and your nickname " \
                       "will be reset to default"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               exampleUsage=exampleUsage,
                               exampleOutput=exampleOutput,
                               aliases=aliases,
                               userPerms=userPerms,
                               botPerms=botPerms,
                               specialCases=specialCases)

    # =================================================
    # Owner
    # =================================================

    @help.command(aliases=['blist'])
    async def blacklist(self, ctx):
        commandName = "Blacklist"
        syntaxMessage = f"`{gcmds.prefix(gcmds, ctx)}blacklist [type] [operation] [ID]`"
        aliases = "`blist`"
        userPerms = "`Bot Owner`"
        specialCases = "Valid Options for Arguments:\n" \
                       "`[type]`: `user` or `guild` *alias for guild is \"server\"*" \
                       "`[operation]`: `add` or `remove`" \
                       "`[ID]`: \nUser --> `user @mention` or `user ID`\nGuild --> `guild ID`"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               aliases=aliases,
                               userPerms=userPerms,
                               specialCases=specialCases)

    @help.command(aliases=['l', 'ld'])
    async def load(self, ctx):
        commandName = "Load"
        syntaxMessage = f"`{gcmds.prefix(gcmds, ctx)}load [extension]`"
        aliases = "`l` `ld`"
        userPerms = "`Bot Owner`"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               aliases=aliases,
                               userPerms=userPerms)

    @help.command(aliases=['ul', 'uld'])
    async def unload(self, ctx):
        commandName = "Unload"
        syntaxMessage = f"`{gcmds.prefix(gcmds, ctx)}unload [extension]`"
        aliases = "`ul` `uld`"
        userPerms = "`Bot Owner`"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               aliases=aliases,
                               userPerms=userPerms)

    @help.command(aliases=['r', 'rl'])
    async def reload(self, ctx):
        commandName = "Reload"
        syntaxMessage = f"`{gcmds.prefix(gcmds, ctx)}reload [optional extension]`"
        aliases = "`r` `rl`"
        userPerms = "`Bot Owner`"
        specialCases = "If `[optional extension]` is not specified, it will reload all currently loaded extensions"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               aliases=aliases,
                               userPerms=userPerms,
                               specialCases=specialCases)

    @help.command(aliases=['taskkill'])
    async def shutdown(self, ctx):
        commandName = "Shutdown"
        syntaxMessage = f"`{gcmds.prefix(gcmds, ctx)}shutdown`"
        aliases = "`taskkill`"
        userPerms = "`Bot Owner`"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               aliases=aliases,
                               userPerms=userPerms)


def setup(client):
    client.add_cog(Help(client))
