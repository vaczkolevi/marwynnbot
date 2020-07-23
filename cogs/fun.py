import random
import os
import re
import discord
from discord.ext import commands


class Fun(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('Cog "fun" has been loaded')

    @commands.command(aliases=['8ball', '8b'])
    async def _8ball(self, ctx, *, question):
        await ctx.message.delete()
        file = open('responses', 'r')
        responses = file.readlines()
        embed = discord.Embed(title='Magic 8 Ball 🎱', color=discord.colour.Color.blue())
        embed.set_thumbnail(url="https://www.horoscope.com/images-US/games/game-magic-8-ball-no-text.png")
        embed.add_field(name='Question', value=f"{ctx.message.author.mention}: " + question, inline=True)
        embed.add_field(name='Answer', value=f'{random.choice(responses)}', inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def choose(self, ctx, *, choices):
        await ctx.message.delete()
        remQuestion = re.sub('[?]', '', str(choices))
        options = remQuestion.split(' or ')
        answer = random.choice(options)
        chooseEmbed = discord.Embed(title='Choose One',
                                    color=discord.Color.blue())
        chooseEmbed.add_field(name=f'{ctx.author} asked: {choices}',
                              value=answer)
        await ctx.channel.send(embed=chooseEmbed)

    @commands.command()
    async def say(self, ctx, *, args):
        sayEmbed = discord.Embed(description=args,
                                 color=discord.Color.blue())
        await ctx.message.delete()
        await ctx.channel.send(embed=sayEmbed)

    @commands.command(aliases=['toadpic', 'toademote'])
    async def toad(self, ctx):
        await ctx.message.delete()
        path = './toad'
        files = os.listdir('./toad')
        name = random.choice(files)
        d = f'{path}//{name}'
        with open(d, 'rb') as f:
            picture = discord.File(f, d)
            toadEmbed = discord.Embed(title='Toad ❤️❤️❤️❤️❤️❤️',
                                      color=discord.Color.red())
            toadEmbed.set_image(url=f"attachment://toad_{name}")
            toadEmbed.set_footer(text=f'{name}, emote name: {name[:-4]}')
        await ctx.channel.send(file=picture, embed=toadEmbed)


def setup(client):
    client.add_cog(Fun(client))
