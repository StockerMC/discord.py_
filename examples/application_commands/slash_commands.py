import typing
import discord

class MyClient(discord.Client):
    def __init__(self):
        # setting the application_id kwarg is required when
        # registering application commands
        super().__init__(application_id=123)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

# setting `guild_ids` in development is better when possible because
# registering global commands has a 1 hour delay
class Avatar(discord.SlashCommand, guild_ids=[123]):
    """Get the avatar of the provided user or yourself"""

    # the `required` kwarg keyword argument can also be set to `False`
    # instead of typehinting the argument as optional
    user: typing.Optional[discord.User] = discord.application_command_option(description='The user to get the avatar from')

    async def callback(self, response: discord.SlashCommandResponse):
        avatar = response.options.user.display_avatar.url
        await response.send_message(avatar, ephemeral=True)

client = MyClient()
client.add_application_command(Avatar())
client.run('token')