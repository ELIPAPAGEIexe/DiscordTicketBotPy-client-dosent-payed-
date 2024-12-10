from discord.ext import commands
from discord import app_commands
from discord.ui import Select, View, Button
import os
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Select, View, Button
import datetime
import io
import discord
from discord.ui import Button

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


TICKET_CATEGORIES = {
   "Support": 1294616242220568636,  
    "HWID": 1294622878393831475,    
   "Media": 1294722808370303116,    
   "Purchase": 1294616100176265271 
}



TICKET_CHANNEL_ID = 1283417834558328853 
ALLOWED_ROLES = [1283411706965528586]   

ALLOWED_CHANNELS = [1297097582220283956, 1297097082712358922, 1297097680677507093, 1297097700483010601]



THUMBNAIL_URL = "https://i.imgur.com/qhkcJIt.png"
FOOTER_TEXT = "Sapphire Tickets"
FOOTER_ICON_URL = "https://i.imgur.com/qhkcJIt.png"

CORRECT_TRANSCRIPT_CHANNEL_ID = 1292872979075567719  


def is_in_allowed_channels(interaction: discord.Interaction) -> bool:
    return interaction.channel.category and interaction.channel.category.id in ALLOWED_CHANNELS

class TicketSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Support", description="Support for our products or any question about our service.", emoji="🛠️"),
            discord.SelectOption(label="HWID", description="Request a HWID reset for any of our products.", emoji="💻"),
            discord.SelectOption(label="Media", description="Apply as a media creator here.", emoji="📋"),
            discord.SelectOption(label="Purchase", description="Purchase products from our store.", emoji="🛒"), 
        ]
        super().__init__(placeholder="Create a new Ticket", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        selected_option = self.values[0] 
        category_id = TICKET_CATEGORIES.get(selected_option)  

        category = discord.utils.get(guild.categories, id=category_id)
        if category is None:
            await interaction.response.send_message("Error: Ticket category not found.", ephemeral=True)
            return

        
        ticket_name = f"{selected_option.lower()}-{interaction.user.name}"

       
        ticket_channel = await guild.create_text_channel(
            name=ticket_name,
            category=category,
            overwrites={
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True),
            }
        )

        
        for role_id in ALLOWED_ROLES:
            role = guild.get_role(role_id)
            if role:
                await ticket_channel.set_permissions(role, view_channel=True)

        
        embed = discord.Embed(
            title=f"Ticket: {ticket_name}",
            description=f"Hey {interaction.user.mention}, support will be with you shortly.",
            color=discord.Color.purple()
        )
        embed.set_thumbnail(url=THUMBNAIL_URL)
        embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON_URL)

        await interaction.response.send_message(f"Ticket created {ticket_channel.mention}", ephemeral=True)
        await ticket_channel.send(embed=embed, view=CloseTicketView(ticket_name, selected_option, interaction.user.name, interaction.user.id))

class CloseTicketButton(Button):
    def __init__(self, ticket_name, category_name, creator_name, creator_id):
        super().__init__(label="Close Ticket", style=discord.ButtonStyle.red)
        self.ticket_name = ticket_name
        self.category_name = category_name
        self.creator_name = creator_name
        self.creator_id = creator_id

    async def callback(self, interaction: discord.Interaction):
       
        transcript_channel = bot.get_channel(CORRECT_TRANSCRIPT_CHANNEL_ID)
        transcript_content = f"Ticket Transcript for {self.ticket_name}:\nCategory: {self.category_name}\nCreator: {self.creator_name} ({self.creator_id})\n"
        
        
        messages = []
        async for msg in interaction.channel.history(limit=100):
            messages.append(f"{msg.author}: {msg.content}")

     
        transcript_text = "\n".join(messages)

       
        transcript_file = io.BytesIO(transcript_text.encode('utf-8'))
        transcript_file.name = f"{self.ticket_name}_transcript.txt"

       
        if transcript_channel:
            await transcript_channel.send(
                content=f"Transcript for ticket {self.ticket_name}",
                file=discord.File(transcript_file, filename=transcript_file.name)
            )

        
        user = await bot.fetch_user(self.creator_id)
        if user:
            embed = discord.Embed(
                title="Ticket Transcript",
                description=f"**Server:** Sapphire\n**Ticket:** {self.ticket_name}\n**Category:** {self.category_name}\n**Creator:** {self.creator_name} ({self.creator_id})\n**Closer:** {interaction.user} ({interaction.user.id})",
                color=discord.Color.purple()
            )
            embed.set_thumbnail(url=THUMBNAIL_URL)
            embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON_URL)

            await user.send(embed=embed)

        
        await interaction.channel.delete(reason="Ticket closed")



class CloseTicketView(View):
    def __init__(self, ticket_name, category_name, creator_name, creator_id):
        super().__init__(timeout=None)
        self.add_item(CloseTicketButton(ticket_name, category_name, creator_name, creator_id))


class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())


@bot.event
async def on_ready():
    print(f"[+] successfully logged in as {bot.user}")

    
    await bot.tree.sync()

    channel = bot.get_channel(TICKET_CHANNEL_ID)

    embed = discord.Embed(
        title="Open a Ticket",
        description=(
            "Choose the subject you want to open a ticket for.\n"
            "### Rules\n"
            "● You may only open one ticket per subject.\n\n"
            "● Do not spam ping staff.\n\n"
            "● Be patient, time will be compensated if you lost some while waiting.\n\n"
            "● If you bought from a reseller, contact them.\n"
        ),
        color=discord.Color.purple()
    )

    embed.set_thumbnail(url=THUMBNAIL_URL)
    embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON_URL)

    if channel:
        await channel.send(embed=embed, view=TicketView())






bot.run('put in here ur bot token and have fun')
