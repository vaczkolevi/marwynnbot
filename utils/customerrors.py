import discord
from discord.ext import commands


class PostgreSQLError(commands.CommandError):
    pass


class NoPostgreSQL(PostgreSQLError):
    """Error raised when no valid db is specified
    """

    def __init__(self):
        self.embed = discord.Embed(title="No Valid DB Connection",
                                   description="No valid DB connection was passed as an argument",
                                   color=discord.Color.dark_red())


class TagError(commands.CommandError):
    def __init__(self, message=None, error=None, *args):
        super().__init__(message=message, *args)
        self.embed = discord.Embed(title="An Error Occurred",
                                   description=f"An error occurred while processing a tag command:\n```{error}\n```",
                                   color=discord.Color.dark_red())


class TagNotFound(TagError):
    """Error raised when user tries to invoke a tag that does not currently exist in the current guild

    Args:
        tag (str): name of the tag
    """

    def __init__(self, tag: str):
        self.embed = discord.Embed(title="Tag Not Found",
                                   description=f"The tag `{tag}` does not exist in this server",
                                   color=discord.Color.dark_red())


class TagAlreadyExists(TagError):
    """Error raised when user tries to create a tag that already exists

    Args:
        tag (str): name of the tag
    """

    def __init__(self, tag: str):
        self.embed = discord.Embed(title="Tag Already Exists",
                                   description=f"The tag `{tag}` already exists in this server",
                                   color=discord.Color.dark_red())


class NotTagOwner(TagError):
    """Error raised when the user tries to edit or delete a tag they do not own

    Args:
        tag (str): name of the tag
    """

    def __init__(self, tag: str):
        self.embed = discord.Embed(title="Illegal Tag Operation",
                                   description=f"You do not own the tag `{tag}`. Modifying or destructive actions can only be performed by the tag's owner",
                                   color=discord.Color.dark_red())


class UserNoTags(TagError):
    """Error raised when the user tries to list a tag but doesn't own any tags

    Args:
        member (discord.Member): the discord.Member instance
    """

    def __init__(self, member: discord.Member):
        self.embed = discord.Embed(title="No Tags Owned",
                                   description=f"{member.mention}, you do not own any tags",
                                   color=discord.Color.dark_red())


class NoSimilarTags(TagError):
    """Error raised when the user searches a tag but no similar or exact results were returned

    Args:
        query (str): the query that the user searched for
    """

    def __init__(self, query: str):
        self.embed = discord.Embed(title="No Results",
                                   description=f"There were no results for any tag named `{query}` in this server",
                                   color=discord.Color.dark_red())


class InvalidTagName(TagError):
    def __init__(self, tag: str):
        self.embed = discord.Embed(title="Invalid Tag Name",
                                   description=f"You cannot create a tag with the name `{tag}`",
                                   color=discord.Color.dark_red())


class TagLimitReached(TagError):
    def __init__(self, user: discord.User):
        self.embed = discord.Embed(title="Tag Limit Reached",
                                   description=f"{user.mention}, you must be a MarwynnBot Premium subscriber in order to "
                                   "create more than 100 tags",
                                   color=discord.Color.dark_red())


class CannotPaginate(commands.CommandError):
    """Error raised when the paginator cannot paginate

    Args:
        message (str): message that will be sent in traceback
    """

    def __init__(self, message):
        self.message = message


class PremiumError(commands.CommandError):
    pass


class NoPremiumGuilds(PremiumError):
    """Error raised when there are no guilds that are MarwynnBot Premium guilds
    """

    def __init__(self):
        self.embed = discord.Embed(title="No MarwynnBot Premium Members",
                                   description="There are no servers registered as MarwynnBot Premium servers \:(",
                                   color=discord.Color.dark_red())


class NoPremiumUsers(PremiumError):
    """Error raised when the current guild contains no MarwynnBot Premium users
    """

    def __init__(self):
        self.embed = discord.Embed(title="No MarwynnBot Premium Members",
                                   description="This server does not have any MarwynnBot Premium members \:(",
                                   color=discord.Color.dark_red())


class NoGlobalPremiumUsers(NoPremiumUsers):
    """Error raised when no user is MarwynnBot Premium
    """

    def __init__(self):
        super().__init__()
        self.embed.description = "There are currently MarwynnBot Premium users"


class NotPremiumGuild(PremiumError):
    """Error raised when the current guild is not a MarwynnBot Premium guild

    Args:
        guild (discord.Guild): the current guild
    """

    def __init__(self, guild: discord.Guild):
        self.embed = discord.Embed(title="Not MarwynnBot Premium",
                                   description=f"This guild, {guild.name}, must have a MarwynnBot Premium Server Subscription"
                                   " to use this command",
                                   color=discord.Color.dark_red())


class NotPremiumUser(PremiumError):
    """Error raised when the current user is not a MarwynnBot Premium user

    Args:
        user (discord.User): the current user
    """

    def __init__(self, user: discord.User):
        self.embed = discord.Embed(title="Not MarwynnBot Premium",
                                   description=f"{user.mention}, you must have a MarwynnBot Premium User Subscription to use this command",
                                   color=discord.Color.dark_red())


class NotPremiumUserOrGuild(PremiumError):
    """Error raised when the current user and guild are both not MarwynnBot Premium

    Args:
        user (discord.User): the current user
        guild (discord.Guild): the current guild
    """

    def __init__(self, user: discord.User, guild: discord.Guild):
        self.embed = discord.Embed(title="Not MarwynnBot Premium",
                                   description=f"{user.mention}, you or this server, {guild.name}, must have a "
                                   "MarwynnBot Premium Server Subscription to use this command",
                                   color=discord.Color.dark_red())


class UserPremiumException(PremiumError):
    """Error raised when there is an exception while performing a premium operation on a user

    Args:
        user (discord.User): the user the error occured with
    """

    def __init__(self, user: discord.User):
        self.embed = discord.Embed(title="Set Premium Error",
                                   description=f"An error occured when trying to operate on {user.display_name}",
                                   color=discord.Color.dark_red())


class UserAlreadyPremium(UserPremiumException):
    """Error raised when the user already has MarwynnBot Premium

    Args:
        user (discord.User): the user the error occured with
    """

    def __init__(self, user: discord.User):
        super().__init__(user)
        self.embed.description = f"{user.display_name} already has a MarwynnBot Premium subscription"


class GuildPremiumException(PremiumError):
    """Error raised when there is an exception while performing a premium operation on a guild

    Args:
        guild (discord.Guild): the guild the error occured with
    """

    def __init__(self, guild: discord.Guild):
        self.embed = discord.Embed(title="Set Premium Error",
                                   description=f"An error occured when trying to operate on {guild.name}",
                                   color=discord.Color.dark_red())


class GuildAlreadyPremium(GuildPremiumException):
    """Error raised when the guild already has MarwynnBot Premium

    Args:
        guild (discord.Guild): the guild the error occured with
    """

    def __init__(self, guild: discord.Guild):
        super().__init__(guild)
        self.embed.description = f"{guild.name} already has a MarwynnBot Premium subscription"


class GameStatsError(commands.CommandError):
    def __init__(self):
        self.embed = discord.Embed(title="GameStats Error",
                                   description="An error occurred while executing a gamestats query",
                                   color=discord.Color.dark_red())


class NoStatsAll(GameStatsError):
    def __init__(self, user: discord.User):
        super().__init__()
        self.embed.description = f"{user.mention}, you do not have any stats for any of MarwynnBot's games. Start playing to see your stats update!"


class NoStatsGame(GameStatsError):
    def __init__(self, user: discord.User, game: str):
        super().__init__()
        self.embed.description = f"{user.mention}, you do not have any stats for the game {game.title()}. Start playing to see your stats update!"
        