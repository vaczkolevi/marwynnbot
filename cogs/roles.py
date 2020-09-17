import asyncio
import json
import re
import os
import discord
from discord.ext import commands
from utils import globalcommands

gcmds = globalcommands.GlobalCMDS()
channel_tag_rx = re.compile(r'<#[0-9]{18}>')
channel_id_rx = re.compile(r'[0-9]{18}')
role_tag_rx = re.compile(r'<@&[0-9]{18}>')
hex_color_rx = re.compile(r'#[A-Fa-f0-9]{6}')
timeout = 180


class Roles(commands.Cog):

    def __init__(self, bot):
        global gcmds
        self.bot = bot
        gcmds = globalcommands.GlobalCMDS(self.bot)
        self.bot.loop.create_task(self.init_rr())

    async def init_rr(self):
        await self.bot.wait_until_ready()
        async with self.bot.db.acquire() as con:
            await con.execute("CREATE TABLE IF NOT EXISTS base_rr(message_id bigint PRIMARY KEY, type text, author_id bigint)")
            await con.execute("CREATE TABLE IF NOT EXISTS emoji_rr(message_id bigint, role_id bigint PRIMARY KEY, emoji text)")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        await self.bot.wait_until_ready()
        async with self.bot.db.acquire() as con:
            result = await con.fetch(f"SELECT * FROM base_rr WHERE message_id={int(payload.message_id)}")
        if not result:
            return

        member = payload.member
        if not member:
            return
        guild_id = payload.guild_id
        event_type = payload.event_type

        if not member.bot and event_type == "REACTION_ADD":
            reacted_emoji = payload.emoji
            message_id = payload.message_id
            channel_id = payload.channel_id
            channel = await self.bot.fetch_channel(channel_id)
            message = await channel.fetch_message(message_id)
            reactions = message.reactions
            guild = await self.bot.fetch_guild(guild_id)
            try:
                users = [(reaction.emoji, await reaction.users().flatten()) for reaction in reactions]
                async with self.bot.db.acquire() as con:
                    role_emoji = await con.fetch(f"SELECT role_id, emoji FROM emoji_rr WHERE message_id={message_id}")
                type_name = result[0]['type']
                for item in role_emoji:
                    role = guild.get_role(int(item['role_id']))
                    if str(reacted_emoji) == str(item['emoji']):
                        if type_name == "normal" or type_name == "single_normal":
                            if role not in member.roles:
                                await member.add_roles(role)
                        if type_name == "reverse":
                            if role in member.roles:
                                await member.remove_roles(role)
                    elif str(reacted_emoji) != str(item['emoji']) and type_name == "single_normal":
                        if role in member.roles:
                            await member.remove_roles(role)
                if type_name == "single_normal":
                    for emoji, user in users:
                        if str(emoji) != str(reacted_emoji):
                            for reacted in user:
                                if member.id == reacted.id:
                                    await message.remove_reaction(emoji, member)
            except (discord.Forbidden, discord.NotFound, KeyError):
                pass

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        await self.bot.wait_until_ready()
        async with self.bot.db.acquire() as con:
            result = await con.fetch(f"SELECT * FROM base_rr WHERE message_id={payload.message_id}")
        if not result:
            return

        guild_id = payload.guild_id
        guild = await self.bot.fetch_guild(guild_id)
        member_id = payload.user_id
        member = await guild.fetch_member(member_id)
        event_type = payload.event_type
        if not member.bot and event_type == "REACTION_REMOVE":
            reacted_emoji = payload.emoji
            message_id = payload.message_id
            try:
                async with self.bot.db.acquire() as con:
                    role_emoji = await con.fetch(f"SELECT role_id, emoji FROM emoji_rr WHERE message_id={message_id}")
                type_name = result[0]['type']
                for item in role_emoji:
                    role = guild.get_role(int(item['role_id']))
                    if str(reacted_emoji) == str(item['emoji']):
                        if type_name == "normal" or type_name == "single_normal":
                            if role in member.roles:
                                await member.remove_roles(role)
                        if type_name == "reverse":
                            if role not in member.roles:
                                await member.add_roles(role)
            except (discord.Forbidden, discord.NotFound, KeyError):
                pass

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            return await self.no_panel(ctx)
        else:
            raise error

    async def check_panel(self, panel: discord.Message) -> discord.Message:
        return panel

    async def edit_panel(self, panel_embed: discord.Embed, panel: discord.Message,
                         title: str = None, description: str = None) -> discord.Message:
        if title:
            panel_embed.title = title
        if description:
            panel_embed.description = description
        return await panel.edit(embed=panel_embed)

    async def no_panel(self, ctx) -> discord.Message:
        embed = discord.Embed(title="Reacton Roles Setup Cancelled",
                              description=f"{ctx.author.mention}, the reaction roles setup was cancelled because the "
                                          f"setup panel was deleted or could not be found",
                              color=discord.Color.dark_red())
        return await ctx.channel.send(embed=embed)

    async def no_message(self, ctx) -> discord.Message:
        embed = discord.Embed(title="No Message Found",
                              description=f"{ctx.author.mention}, no reaction roles panel was found for that message ID",
                              color=discord.Color.dark_red())
        return await ctx.channel.send(embed=embed, delete_after=5)

    async def user_cancelled(self, ctx, panel: discord.Message) -> discord.Message:
        embed = discord.Embed(title="Reaction Roles Setup Cancelled",
                              description=f"{ctx.author.mention}, you have cancelled reaction roles setup",
                              color=discord.Color.dark_red())
        panel_message = await self.check_panel(panel)
        if not panel_message:
            return await ctx.channel.send(embed=embed, delete_after=10)
        else:
            return await panel_message.edit(embed=embed, delete_after=10)

    async def timeout(self, ctx, timeout: int, panel: discord.Message) -> discord.Message:
        embed = discord.Embed(title="Reaction Roles Setup Cancelled",
                              description=f"{ctx.author.mention}, the reaction roles setup was canelled because you "
                                          f"did not provide a valid action within {timeout} seconds",
                              color=discord.Color.dark_red())
        panel_message = await self.check_panel(panel)
        if not panel_message:
            return await ctx.channel.send(embed=embed, delete_after=10)
        else:
            return await panel_message.edit(embed=embed, delete_after=10)

    async def success(self, ctx, success_str: str) -> discord.Message:
        embed = discord.Embed(title=f"Successfully {success_str.title()} Reaction Role Panel",
                              description=f"{ctx.author.mention}, your reaction role panel was successfully"
                                          f" {success_str}",
                              color=discord.Color.blue())
        return await ctx.channel.send(embed=embed)

    async def failure(self, ctx, success_str: str) -> discord.Message:
        embed = discord.Embed(title=f"Failed to {success_str.title()} Reaction Role Panel",
                              description=f"{ctx.author.mention}, your reaction role panel could not be"
                                          f" {success_str}ed",
                              color=discord.Color.dark_red())
        return await ctx.channel.send(embed=embed)

    async def send_rr_message(self, ctx, channel: discord.TextChannel, send_embed: discord.Embed,
                              role_emoji: list, type_name: str):
        rr_message = await channel.send(embed=send_embed)
        async with self.bot.db.acquire() as con:
            await con.execute(f"INSERT INTO base_rr(message_id, type, author_id) VALUES ({rr_message.id}, $tag${type_name}$tag$, {ctx.author.id})")
            for role, emoji in role_emoji:
                await rr_message.add_reaction(emoji)
                await con.execute(f"INSERT INTO emoji_rr(message_id, role_id, emoji) VALUES {rr_message.id}, {role.id}, $tag${emoji}$tag$")
        return

    async def edit_rr_message(self, ctx, message_id: int, guild_id: int, title: str, description: str, color: str,
                              emoji_role_list, type_name):
        for text_channel in ctx.guild.text_channels:
            try:
                message = await text_channel.fetch_message(message_id)
                break
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                pass

        embed = discord.Embed(title=title,
                              description=description,
                              color=color)
        try:
            await message.edit(embed=embed)
        except discord.NotFound:
            return await self.failure(ctx, "edit")

        if emoji_role_list or type_name:
            async with self.bot.db.acquire() as con:
                if emoji_role_list:
                    await message.clear_reactions()
                    await con.execute(f"DELETE FROM emoji_rr WHERE message_id={message.id}")
                    for role, emoji in emoji_role_list:
                        await message.add_reaction(emoji)
                        await con.execute(f"INSERT INTO emoji_rr(message_id, role_id, emoji) VALUES {message.id}, {role.id}, $tag${emoji}$tag$")
                if type_name:
                    await con.execute(f"UPDATE base_rr SET type=$tag${type_name}$tag$ WHERE message_id={message.id}")
        return

    async def check_rr_author(self, message_id: int, user_id: int) -> bool:
        async with self.bot.db.acquire() as con:
            result = await con.fetch(f"SELECT * FROM base_rr WHERE message_id={message_id} AND author_id={user_id}")
        return True if result else False

    async def check_rr_exists(self, ctx, message_id: int):
        async with self.bot.db.acquire() as con:
            result = await con.fetch(f"SELECT * FROM base_rr WHERE message_id={message_id}")
        return True if result else False

    async def get_rr_info(self, ctx, message_id: int) -> discord.Embed:
        found = False
        for text_channel in ctx.guild.text_channels:
            try:
                message = await text_channel.fetch_message(message_id)
                found = True
                break
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                continue
        if found:
            embed = message.embeds[0]
            return embed
        else:
            return None

    async def delete_rr_message(self, ctx, message_id: int):
        found = False
        for text_channel in ctx.guild.text_channels:
            try:
                message = await text_channel.fetch_message(message_id)
                found = True
                break
            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                continue

        if found:
            title = "Successfully Deleted Reaction Role"
            description = f"{ctx.author.mention}, I have deleted the reaction roles panel and cleared the record from " \
                          f"my database "
            color = discord.Color.blue()
            try:
                await gcmds.smart_delete(message)
            except discord.Forbidden:
                title = "404 Forbidden"
                description = f"{ctx.author}, I could not delete the reaction roles panel"
                color = discord.Color.dark_red()

            async with self.bot.db.acquire() as con:
                await con.execute(f"DELETE FROM base_rr WHERE message_id={message.id}")
                await con.execute(f"DELETE FROM emoji_rr WHERE message_id={message.id}")

            embed = discord.Embed(title=title,
                                  description=description,
                                  color=color)
            return await ctx.channel.send(embed=embed)

    async def get_rr_type(self, message_id: int) -> str:
        async with self.bot.db.acquire() as con:
            type = await con.fetchval(f"SELECT type FROM base_rr WHERE message_id={message_id}")
        return type.replace("_", " ").title()

    @commands.group(aliases=['rr'])
    @commands.bot_has_permissions(manage_roles=True, add_reactions=True)
    @commands.has_permissions(manage_guild=True)
    async def reactionrole(self, ctx):

        if not ctx.invoked_subcommand:
            message_id_message = f"The `[messageID]` argument must be the message ID of a reaction " \
                                 f"roles panel that you have created. You will be unable to edit the panel if you " \
                                 f"provide an invalid message ID or provide a message ID of a panel that was " \
                                 f"not created by you"
            embed = discord.Embed(title="ReactionRoles Help Menu",
                                  description=f"All reaction roles commands can be accessed using "
                                              f"`{await gcmds.prefix(ctx)}reactionrole [option]`. "
                                              f"Below is a list of all the valid options",
                                  color=discord.Color.blue())
            embed.add_field(name="Create",
                            value=f"**Usage:** `{await gcmds.prefix(ctx)}reactionrole create`\n"
                                  f"**Returns:** Interactive reaction roles setup panel\n"
                                  f"**Aliases:** `-c` `start` `make`")
            embed.add_field(name="Edit",
                            value=f"**Usage:** `{await gcmds.prefix(ctx)}reactionrole edit [messageID]`\n"
                                  f"**Returns:** Interactive reaction roles edit panel\n"
                                  f"**Aliases:** `-e` `adjust`\n"
                                  f"**Special Cases:** {message_id_message}",
                            inline=False)
            embed.add_field(name="Delete",
                            value=f"**Usage:** `{await gcmds.prefix(ctx)}reactionrole delete [messageID]`\n"
                                  f"**Returns:** Message that details status of the deletion\n"
                                  f"**Aliases:** `-d` `-rm` `del`\n"
                                  f"**Special Cases:** {message_id_message}. If the panel was manually deleted, "
                                  f"MarwynnBot will delete the panel's record from its database of reaction role panels",
                            inline=False)
            embed.add_field(name="Useful Resources",
                            value="**Hex Color Picker:** https://www.google.com/search?q=color+picker",
                            inline=False)
            return await ctx.channel.send(embed=embed)

    @reactionrole.command(aliases=['-c', 'start', 'make'])
    async def create(self, ctx):

        panel_embed = discord.Embed(title="Reaction Role Setup Menu",
                                    description=f"{ctx.author.mention}, welcome to MarwynnBot's reaction role setup "
                                                f"menu. Just follow the prompts and you will have a working reaction "
                                                f"roles panel!",
                                    color=discord.Color.blue())
        panel_embed.set_footer(text="Type \"cancel\" to cancel at any time")
        panel = await ctx.channel.send(embed=panel_embed)

        await asyncio.sleep(5.0)

        def from_user(message: discord.Message) -> bool:
            if message.author == ctx.author and message.channel == ctx.channel:
                return True
            else:
                return False

        def panel_react(reaction: discord.Reaction, user: discord.User) -> bool:
            if reaction.message.id == panel.id and ctx.author.id == user.id:
                return True
            else:
                return False

        # User will input the channel by tag
        while True:
            try:
                panel_message = await self.check_panel(panel)
                if not panel_message:
                    return await self.no_panel(ctx)
                await self.edit_panel(panel_embed, panel_message, title=None,
                                      description=f"{ctx.author.mention}, please tag the channel you would like the "
                                                  f"embed to be sent in (or type its ID)")
                result = await self.bot.wait_for("message", check=from_user,
                                                 timeout=timeout)
            except asyncio.TimeoutError:
                return await self.timeout(ctx, timeout, panel)
            if not re.match(channel_tag_rx, result.content):
                if re.match(channel_id_rx, result.content):
                    channel_id = result.content
                    break
                else:
                    if result.content == "cancel":
                        return await self.user_cancelled(ctx, panel_message)
                    continue
            else:
                channel_id = result.content[2:20]
            break
        await gcmds.smart_delete(result)

        channel = await commands.AutoShardedBot.fetch_channel(self.bot, channel_id)

        # User will input the embed title
        try:
            panel_message = await self.check_panel(panel)
            if not panel_message:
                return await self.no_panel(ctx)
            await self.edit_panel(panel_embed, panel_message, title=None,
                                  description=f"{ctx.author.mention}, please enter the title of the embed that will "
                                              f"be sent")
            result = await self.bot.wait_for("message", check=from_user, timeout=timeout)
        except asyncio.TimeoutError:
            return await self.timeout(ctx, timeout, panel)
        else:
            if result.content == "cancel":
                return await self.user_cancelled(ctx, panel_message)
        await gcmds.smart_delete(result)

        title = result.content

        # User will input the embed description
        try:
            panel_message = await self.check_panel(panel)
            if not panel_message:
                return await self.no_panel(ctx)
            await self.edit_panel(panel_embed, panel_message, title=None,
                                  description=f"{ctx.author.mention}, please enter the description of the embed that "
                                              f"will be sent")
            result = await self.bot.wait_for("message", check=from_user, timeout=timeout)
        except asyncio.TimeoutError:
            return await self.timeout(ctx, timeout, panel)
        else:
            if result.content == "cancel":
                return await self.user_cancelled(ctx, panel_message)
        await gcmds.smart_delete(result)

        description = result.content

        # User will input the embed color
        while True:
            try:
                panel_message = await self.check_panel(panel)
                if not panel_message:
                    return await self.no_panel(ctx)
                await self.edit_panel(panel_embed, panel_message, title=None,
                                      description=f"{ctx.author.mention}, please enter the hex color of the embed "
                                                  f"that will be sent")
                result = await self.bot.wait_for("message", check=from_user,
                                                 timeout=timeout)
            except asyncio.TimeoutError:
                return await self.timeout(ctx, timeout, panel)
            if not re.match(hex_color_rx, result.content):
                if result.content == "cancel":
                    return await self.user_cancelled(ctx, panel_message)
                else:
                    continue
            break
        await gcmds.smart_delete(result)

        color = int(result.content[1:], 16)

        # User will tag the role, then react with the corresponding emoji
        emoji_role_list = []
        emoji_list = []
        while True:
            while True:
                try:
                    panel_message = await self.check_panel(panel)
                    if not panel_message:
                        return await self.no_panel(ctx)
                    await self.edit_panel(panel_embed, panel_message, title=None,
                                          description=f"{ctx.author.mention}, please tag the role you would like to be "
                                                      f"added into the reaction role or type *finish* to finish setup")
                    result = await self.bot.wait_for("message", check=from_user,
                                                     timeout=timeout)
                except asyncio.TimeoutError:
                    return await self.timeout(ctx, timeout, panel)
                if not re.match(role_tag_rx, result.content):
                    if result.content == "cancel":
                        return await self.user_cancelled(ctx, panel_message)
                    elif result.content == "finish":
                        break
                    else:
                        continue
                else:
                    break
            if result.content == "finish":
                await gcmds.smart_delete(result)
                break

            role = result.content[3:21]

            while True:
                try:
                    panel_message = await self.check_panel(panel)
                    if not panel_message:
                        return await self.no_panel(ctx)
                    await self.edit_panel(panel_embed, panel_message, title=None,
                                          description=f"{ctx.author.mention}, please react to this panel with the emoji"
                                                      f" you want the user to react with to get the role <@&{role}>")
                    result = await self.bot.wait_for("reaction_add", check=panel_react,
                                                     timeout=timeout)
                except asyncio.TimeoutError:
                    return await self.timeout(ctx, timeout, panel)
                if result[0].emoji in emoji_list:
                    continue
                else:
                    break

            emoji = result[0].emoji
            emoji_list.append(emoji)
            await result[0].message.clear_reactions()

            emoji_role_list.append((role, emoji))

        # User will input number to dictate type of reaction role
        while True:
            try:
                panel_message = await self.check_panel(panel)
                if not panel_message:
                    return await self.no_panel(ctx)
                await self.edit_panel(panel_embed, panel_message, title=None,
                                      description=f"{ctx.author.mention}, please enter the number that corresponds to "
                                                  f"the type of reaction role behavior you would like\n\n"
                                                  f"**1:** Normal *(react to add, unreact to remove, multiple at a "
                                                  f"time)*\n "
                                                  f"**2:** Reverse *(react to remove, unreact to add, multiple at a "
                                                  f"time)*\n "
                                                  f"**3:** Single Normal *(same as normal, except you can only have one"
                                                  f" role at a time)*\n\n"
                                                  f"*If I wanted to pick `Normal`, I would type \"1\" as the response*")
                result = await self.bot.wait_for("message", check=from_user,
                                                 timeout=timeout)
            except asyncio.TimeoutError:
                return await self.timeout(ctx, timeout, panel)
            else:
                if result.content == "cancel":
                    return await self.user_cancelled(ctx, panel_message)
                if result.content == "1":
                    type_name = "normal"
                    break
                if result.content == "2":
                    type_name = "reverse"
                    break
                if result.content == "3":
                    type_name = "single_normal"
                    break
                continue
        await gcmds.smart_delete(result)

        type_name = type_name

        await panel.delete()

        await self.success(ctx, "created")

        # Post reaction role panel in the channel
        rr_embed = discord.Embed(title=title,
                                 description=description,
                                 color=color)
        return await self.send_rr_message(ctx, channel, rr_embed, emoji_role_list, type_name)

    @reactionrole.command(aliases=['adjust', '-e'])
    async def edit(self, ctx, message_id: int = None):
        if not message_id:
            return await ctx.invoke(self.reactionrole)

        exists = await self.check_rr_exists(ctx, message_id)
        if not exists:
            return await self.no_message(ctx)

        is_author = await self.check_rr_author(message_id, ctx.author.id)
        if not is_author:
            not_author = discord.Embed(title="Not Panel Author",
                                       description=f"{ctx.author.mention}, you must be the author of that reaction "
                                                   f"roles panel to edit the panel",
                                       color=discord.Color.dark_red())
            return await ctx.channel.send(embed=not_author, delete_after=10)

        panel_embed = discord.Embed(title="Reaction Role Setup Menu",
                                    description=f"{ctx.author.mention}, welcome to MarwynnBot's reaction role setup "
                                                f"menu. Just follow the prompts to edit your panel!",
                                    color=discord.Color.blue())
        panel_embed.set_footer(text="Type \"cancel\" to cancel at any time")
        panel = await ctx.channel.send(embed=panel_embed)

        await asyncio.sleep(5.0)

        old_embed = await self.get_rr_info(ctx, message_id)
        if not old_embed:
            return await self.no_message(ctx)

        def from_user(message: discord.Message) -> bool:
            if message.author == ctx.author and message.channel == ctx.channel:
                return True
            else:
                return False

        def panel_react(reaction: discord.Reaction, user: discord.User) -> bool:
            if reaction.message.id == panel.id and ctx.author.id == user.id:
                return True
            else:
                return False

        # User provides the panel's new title
        try:
            panel_message = await self.check_panel(panel)
            if not panel_message:
                return await self.no_panel(ctx)
            await self.edit_panel(panel_embed, panel_message, title=None,
                                  description=f"{ctx.author.mention}, please enter the new title of the embed, "
                                              f"or enter *\"skip\"* to keep the current title\n\n**Current Title:**\n"
                                              f"{old_embed.title}")
            result = await self.bot.wait_for("message", check=from_user, timeout=timeout)
        except asyncio.TimeoutError:
            return await self.timeout(ctx, timeout, panel)
        else:
            if result.content == "cancel":
                return await self.user_cancelled(ctx, panel_message)
            elif result.content == "skip":
                title = old_embed.title
            else:
                title = result.content
        await gcmds.smart_delete(result)

        # User provides the panel's new description
        try:
            panel_message = await self.check_panel(panel)
            if not panel_message:
                return await self.no_panel(ctx)
            await self.edit_panel(panel_embed, panel_message, title=None,
                                  description=f"{ctx.author.mention}, please enter the new description of the "
                                              f"embed, or enter *\"skip\"* to keep the current "
                                              f"description\n\n**Current Description:**\n{old_embed.description}")
            result = await self.bot.wait_for("message", check=from_user,
                                             timeout=timeout)
        except asyncio.TimeoutError:
            return await self.timeout(ctx, timeout, panel)
        else:
            if result.content == "cancel":
                return await self.user_cancelled(ctx, panel_message)
            elif result.content == "skip":
                description = old_embed.description
            else:
                description = result.content
        await gcmds.smart_delete(result)

        # User will input the embed color
        while True:
            try:
                panel_message = await self.check_panel(panel)
                if not panel_message:
                    return await self.no_panel(ctx)
                await self.edit_panel(panel_embed, panel_message, title=None,
                                      description=f"{ctx.author.mention}, please enter the new hex color of the "
                                                  f"embed, or enter *\"skip\"* to keep the current "
                                                  f"color\n\n**Current Color:**\n{str(old_embed.color)}")
                result = await self.bot.wait_for("message", check=from_user,
                                                 timeout=timeout)
            except asyncio.TimeoutError:
                return await self.timeout(ctx, timeout, panel)
            if not re.match(hex_color_rx, result.content):
                if result.content == "cancel":
                    return await self.user_cancelled(ctx, panel_message)
                elif result.content == "skip":
                    color = old_embed.color
                    break
                else:
                    continue
            else:
                color = int(result.content[1:], 16)
                break
        await gcmds.smart_delete(result)

        # User will tag the role, then react with the corresponding emoji
        emoji_role_list = []
        emoji_list = []
        while True:
            while True:
                try:
                    panel_message = await self.check_panel(panel)
                    if not panel_message:
                        return await self.no_panel(ctx)
                    await self.edit_panel(panel_embed, panel_message, title=None,
                                          description=f"{ctx.author.mention}, please tag the role you would like the "
                                          "reaction role panel to have, type *finish* to finish setup, "
                                          "or type *skip* to keep the current roles and reactions\n\n**Specifying a "
                                          "role will not add it to the current list. You must specify all the roles "
                                          "that this panel should have (including already added roles)**")
                    result = await self.bot.wait_for("message", check=from_user,
                                                     timeout=timeout)
                except asyncio.TimeoutError:
                    return await self.timeout(ctx, timeout, panel)
                if not re.match(role_tag_rx, result.content):
                    if result.content == "cancel":
                        return await self.user_cancelled(ctx, panel_message)
                    elif result.content == "finish":
                        break
                    elif result.content == "skip":
                        break
                    else:
                        continue
                else:
                    break

            await gcmds.smart_delete(result)
            if result.content == "finish" or result.content == "skip":
                break

            role = result.content[3:21]

            while True:
                try:
                    panel_message = await self.check_panel(panel)
                    if not panel_message:
                        return await self.no_panel(ctx)
                    await self.edit_panel(panel_embed, panel_message, title=None,
                                          description=f"{ctx.author.mention}, please react to this panel with the emoji"
                                                      f" you want the user to react with to get the role <@&{role}>")
                    result = await self.bot.wait_for("reaction_add",
                                                     check=panel_react,
                                                     timeout=timeout)
                except asyncio.TimeoutError:
                    return await self.timeout(ctx, timeout, panel)
                if result[0].emoji in emoji_list:
                    continue
                else:
                    break

            emoji = result[0].emoji
            emoji_list.append(emoji)
            await result[0].message.clear_reactions()

            emoji_role_list.append((role, emoji))

        if result.content == "skip" or (result.content == "finish" and not emoji_list and not emoji_role_list):
            emoji_list = None
            emoji_role_list = None

        # User will input number to dictate type of reaction role
        while True:
            try:
                panel_message = await self.check_panel(panel)
                if not panel_message:
                    return await self.no_panel(ctx)
                await self.edit_panel(panel_embed, panel_message, title=None,
                                      description=f"{ctx.author.mention}, please enter the number that corresponds to "
                                                  f"the type of reaction role behavior you would like, or type *skip* "
                                                  f"to keep the current type\nCurrent type: "
                                                  f"{await self.get_rr_type(message_id, ctx.guild.id)}\n\n "
                                                  f"**1:** Normal *(react to add, unreact to remove, multiple at a "
                                                  f"time)*\n "
                                                  f"**2:** Reverse *(react to remove, unreact to add, multiple at a "
                                                  f"time)*\n "
                                                  f"**3:** Single Normal *(same as normal, except you can only have one"
                                                  f" role at a time)*\n\n"
                                                  f"*If I wanted to pick `Normal`, I would type \"1\" as the response*")
                result = await self.bot.wait_for("message", check=from_user,
                                                 timeout=timeout)
            except asyncio.TimeoutError:
                return await self.timeout(ctx, timeout, panel)
            else:
                if result.content == "cancel":
                    return await self.user_cancelled(ctx, panel_message)
                if result.content == "skip":
                    break
                if result.content == "1":
                    type_name = "normal"
                    break
                if result.content == "2":
                    type_name = "reverse"
                    break
                if result.content == "3":
                    type_name = "single_normal"
                    break
                continue
        await gcmds.smart_delete(result)

        if result.content == "skip":
            type_name = None
        else:
            type_name = type_name

        await panel.delete()

        await self.success(ctx, "edited")

        return await self.edit_rr_message(ctx, message_id, ctx.guild.id, title, description,
                                          color, emoji_role_list, type_name)

    @reactionrole.command(aliases=['-d', '-rm', 'del'])
    async def delete(self, ctx, message_id: int = None):
        if not message_id:
            return await ctx.invoke(self.reactionrole)

        exists = await self.check_rr_exists(ctx, message_id)
        if not exists:
            return await self.no_message(ctx)

        is_author = await self.check_rr_author(message_id, ctx.author.id)
        if not is_author:
            not_author = discord.Embed(title="Not Panel Author",
                                       description=f"{ctx.author.mention}, you must be the author of that reaction "
                                                   f"roles panel to edit the panel",
                                       color=discord.Color.dark_red())
            return await ctx.channel.send(embed=not_author, delete_after=10)

        return await self.delete_rr_message(ctx, message_id)


def setup(bot):
    bot.add_cog(Roles(bot))
