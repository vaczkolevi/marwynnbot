from datetime import datetime
import praw
import yaml
import random
import discord
from discord.ext import commands
from globalcommands import GlobalCMDS as gcmds


class Reddit(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Cog "{self.qualified_name}" has been loaded')

    async def get_id_secret(self, ctx):
        try:
            with open('./reddit_api.yaml', 'r') as f:
                stream = yaml.full_load(f)
                client_id = stream[str('client_id')]
                client_secret = stream[str('client_secret')]
                user_agent = stream[str('user_agent')]
            return [client_id, client_secret, user_agent]

        except FileNotFoundError:
            with open('reddit_api.yaml', 'w') as f:
                f.write('client_id: CLIENT_ID_FROM_REDDIT_APPLICATION\nclient_secret: '
                        'CLIENT_SECRET_FROM_REDDIT_APPLICATION')
            title = "Created File"
            description = "The file `reddit_api.yaml` was created. Insert your Reddit application's client ID and " \
                          "secret in the placeholder "
            color = discord.Color.red()
            embed = discord.Embed(title=title,
                                  description=description,
                                  color=color)
            await ctx.channel.send(embed=embed, delete_after=10)
            return None

    async def embed_template(self, ctx):
        info = await self.get_id_secret(ctx)

        if not info:
            return

        reddit = praw.Reddit(client_id=info[0],
                             client_secret=info[1],
                             user_agent=info[2])
        picture_search = reddit.subreddit(ctx.command.name).hot()

        submissions = []

        for post in picture_search:
            if len(submissions) == 300:
                break
            elif (not post.stickied and not post.over_18) and not "https://v.redd.it/" in post.url:
                submissions.append(post)

        picture = random.choice(submissions)

        web_link = f"https://www.reddit.com/{picture.permalink}"
        url = picture.url
        author = picture.author
        author_url = f"https://www.reddit.com/user/{author}/"
        author_icon_url = picture.author.icon_img
        created_timestamp = datetime.fromtimestamp(picture.created_utc)
        real_timestamp = created_timestamp.strftime("%d/%m/%Y %H:%M:%S")
        num_comments = picture.num_comments
        upvotes = picture.score
        ratio = picture.upvote_ratio * 100
        sub_name = picture.subreddit_name_prefixed
        embed = discord.Embed(title=sub_name,
                              url=web_link,
                              color=discord.Color.blue())
        embed.set_author(name=author, url=author_url, icon_url=author_icon_url)
        embed.set_image(url=url)
        embed.set_footer(
            text=f"⬆️{upvotes}️ ({ratio}%)\n💬{num_comments}\n🕑{real_timestamp}\n"
                 f"Copyrights belong to their respective owners")
        await ctx.channel.send(embed=embed)

    @commands.command(aliases=['reddithelp'])
    async def reddit(self, ctx, cmdName=None):
        await gcmds.invkDelete(gcmds, ctx)

        CMDLIST = self.get_commands()
        del CMDLIST[0]
        CMDNAMES = [i.name for i in CMDLIST]
        description = f"Do `{gcmds.prefix(gcmds, ctx)}reddit [cmdName]` to get the usage of that particular " \
                      f"command.\n\n**List of all {len(CMDLIST)} reddit commands:**\n\n `{'` `'.join(sorted(CMDNAMES))}` "
        if cmdName is None or cmdName == "reddit":
            helpEmbed = discord.Embed(title="Reddit Commands Help",
                                      description=description,
                                      color=discord.Color.blue())
        else:
            if cmdName in CMDNAMES:
                r_command = cmdName.capitalize()
                helpEmbed = discord.Embed(title=f"{r_command}",
                                          description=f"Returns a randomly selected image from the subreddit r/{cmdName}",
                                          color=discord.Color.blue())
                helpEmbed.add_field(name="Usage",
                                    value=f"`{gcmds.prefix(gcmds, ctx)}{cmdName}`",
                                    inline=False)
                pot_alias = self.client.get_command(name=cmdName)
                aliases = [g for g in pot_alias.aliases]
                if aliases:
                    value = "`" + "` `".join(sorted(aliases)) + "`"
                    helpEmbed.add_field(name="Aliases",
                                        value=value,
                                        inline=False)
            else:
                helpEmbed = discord.Embed(title="Command Not Found",
                                          description=f"{ctx.author.mention}, {cmdName} is not a valid reddit command",
                                          color=discord.Color.blue())
        await ctx.channel.send(embed=helpEmbed)

    @commands.command(aliases=['abj', 'meananimals'])
    async def animalsbeingjerks(self, ctx):
        await gcmds.invkDelete(gcmds, ctx)
        await self.embed_template(ctx)
        return

    @commands.command(aliases=['anime'])
    async def awwnime(self, ctx):
        await gcmds.invkDelete(gcmds, ctx)
        await self.embed_template(ctx)
        return

    @commands.command(aliases=['car', 'cars', 'carpics'])
    async def carporn(self, ctx):
        await gcmds.invkDelete(gcmds, ctx)
        await self.embed_template(ctx)
        return

    @commands.command()
    async def cosplay(self, ctx):
        await gcmds.invkDelete(gcmds, ctx)
        await self.embed_template(ctx)
        return

    @commands.command(aliases=['earth', 'earthpics'])
    async def earthporn(self, ctx):
        await gcmds.invkDelete(gcmds, ctx)
        await self.embed_template(ctx)
        return

    @commands.command(aliases=['food', 'foodpics'])
    async def foodporn(self, ctx):
        await gcmds.invkDelete(gcmds, ctx)
        await self.embed_template(ctx)
        return

    @commands.command(aliases=['animemes'])
    async def goodanimemes(self, ctx):
        await gcmds.invkDelete(gcmds, ctx)
        await self.embed_template(ctx)
        return

    @commands.command(aliases=['history', 'historypics'])
    async def historyporn(self, ctx):
        await gcmds.invkDelete(gcmds, ctx)
        await self.embed_template(ctx)
        return

    @commands.command(aliases=['pic', 'itap'])
    async def itookapicture(self, ctx):
        await gcmds.invkDelete(gcmds, ctx)
        await self.embed_template(ctx)
        return

    @commands.command(aliases=['map', 'maps', 'mappics'])
    async def mapporn(self, ctx):
        await gcmds.invkDelete(gcmds, ctx)
        await self.embed_template(ctx)
        return

    @commands.command(aliases=['interesting', 'mi'])
    async def mildlyinteresting(self, ctx):
        await gcmds.invkDelete(gcmds, ctx)
        await self.embed_template(ctx)
        return

    @commands.command()
    async def pareidolia(self, ctx):
        await gcmds.invkDelete(gcmds, ctx)
        await self.embed_template(ctx)
        return

    @commands.command(aliases=['ptiming'])
    async def perfecttiming(self, ctx):
        await gcmds.invkDelete(gcmds, ctx)
        await self.embed_template(ctx)
        return

    @commands.command(aliases=['psbattle'])
    async def photoshopbattles(self, ctx):
        await gcmds.invkDelete(gcmds, ctx)
        await self.embed_template(ctx)
        return

    @commands.command(aliases=['quotes'])
    async def quotesporn(self, ctx):
        await gcmds.invkDelete(gcmds, ctx)
        await self.embed_template(ctx)
        return

    @commands.command(aliases=['room', 'rooms', 'roompics'])
    async def roomporn(self, ctx):
        await gcmds.invkDelete(gcmds, ctx)
        await self.embed_template(ctx)
        return

    @commands.command()
    async def tumblr(self, ctx):
        await gcmds.invkDelete(gcmds, ctx)
        await self.embed_template(ctx)
        return

    @commands.command()
    async def unexpected(self, ctx):
        await gcmds.invkDelete(gcmds, ctx)
        await self.embed_template(ctx)
        return

    @commands.command(aliases=['wallpaper'])
    async def wallpapers(self, ctx):
        await gcmds.invkDelete(gcmds, ctx)
        await self.embed_template(ctx)
        return

    @commands.command(aliases=['woah'])
    async def woahdude(self, ctx):
        await gcmds.invkDelete(gcmds, ctx)
        await self.embed_template(ctx)
        return


def setup(client):
    client.add_cog(Reddit(client))