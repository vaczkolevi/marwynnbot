import discord
from discord.ext import commands
from mcstatus import MinecraftServer
from utils import globalcommands

gcmds = globalcommands.GlobalCMDS()


class Minecraft(commands.Cog):

    def __init__(self, bot):
        global gcmds
        self.bot = bot
        gcmds = globalcommands.GlobalCMDS(self.bot)

    async def get_server(self, host: str) -> MinecraftServer:
        try:
            return MinecraftServer.lookup(host)
        except Exception:
            return None

    async def get_ping(self, ctx, host: str) -> discord.Message:
        server = await self.get_server(host)
        if not server:
            return None

        try:
            latency = server.ping()
        except Exception:
            latency_str = "Could not reach server"
        else:
            latency_str = f"The server replied in {latency} ms"
        embed = discord.Embed(title=f"Ping for {host}",
                              description=latency_str,
                              color=discord.Color.blue())
        return await ctx.channel.send(embed=embed)

    async def get_query(self, ctx, host: str) -> discord.Message:
        server = await self.get_server(host)
        if not server:
            return None
        try:
            status = server.query()
        except Exception:
            embed = discord.Embed(title="Request Timed Out",
                                  description=f"{ctx.author.mention}, your request was timed out. Please try again later",
                                  color=discord.Color.dark_red())
            return await ctx.channel.send(embed=embed)
        players_online = f"Players Online: `{status.players.online}`"
        max_players = f"Max Players: `{status.players.max}`"
        software = f"Software: `{status.software.brand.title()} {status.software.version}`"
        if not status.software.plugins:
            plugins = "Plugins: `N/A`"
        else:
            plugins = f"Plugins: `{'` `'.join(status.software.plugins)}"
        motd = f"MOTD: `{status.motd}`"

        items_list = [players_online, max_players, software, plugins, motd]

        embed = discord.Embed(title=f"Details for {host}",
                              description=f"{ctx.author.mention}, here are the details for the requested server\n\n",
                              color=discord.Color.blue())
        embed.description += "\n".join(items_list)
        return await ctx.channel.send(embed=embed)

    async def invalid(self, ctx, host: str) -> discord.Message:
        embed = discord.Embed(title="Invalid Server",
                              description=f"{ctx.author.mention}, no server exists for hostname {host}",
                              color=discord.Color.dark_red())
        return await ctx.channel.send(embed=embed)

    @commands.group(invoke_without_command=True,
                    aliases=['mc'],
                    desc="Displays the help command for minecraft",
                    note="Subcommands can be used once every 10 seconds per member")
    async def minecraft(self, ctx):
        embed = discord.Embed(title="Minecraft Commands Help",
                                description=f"Access MarwynnBot's Minecraft commands using "
                                            f"`{await gcmds.prefix(ctx)}minecraft [option]`. Here is a list of all "
                                            f"the available options",
                                color=discord.Color.blue())
        embed.add_field(name="Ping",
                        value=f"Usage: `{await gcmds.prefix(ctx)}minecraft ping [serverIP]`\n"
                                f"Returns: The ping of the specified minecraft server\n"
                                f"Aliases: `-p`",
                        inline=False)
        embed.add_field(name="Details",
                        value=f"Usage: `{await gcmds.prefix(ctx)}minecraft details [serverIP]`\n"
                                f"Returns: Details about the specified minecraft server\n"
                                f"Aliases: `-d` `-q` `query`",
                        inline=False)
        embed.add_field(name="Special Cases",
                        value=f"Special Cases: The `[serverIP]` argument can be a domain name, IP address, "
                                f"or IP address:port",
                        inline=False)
        await ctx.channel.send(embed=embed)

    @minecraft.command(aliases=['-p'])
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def ping(self, ctx, host: str = None):
        if not host:
            return await ctx.invoke(self.minecraft)

        if not await self.get_ping(ctx, host):
            return await self.invalid(ctx, host)

    @minecraft.command(aliases=['-d', '-q', 'query'])
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def details(self, ctx, host: str = None):
        if not host:
            return await ctx.invoke(self.minecraft)

        if not await self.get_query(ctx, host):
            return await self.invalid(ctx, host)


def setup(bot):
    bot.add_cog(Minecraft(bot))
