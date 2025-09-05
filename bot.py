import discord
from discord.ext import commands
import sqlite3
import asyncio
import json
import os
from datetime import datetime
import logging
from typing import Optional
import sys

# Get server-specific configuration from environment
SERVER_ID = os.getenv('SERVER_ID', 'default')
GUILD_ID = os.getenv('GUILD_ID')
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Bot setup
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Server-specific database name
db_name = f'mystic_{SERVER_ID}.db' if SERVER_ID != 'default' else 'mystic.db'

# Database setup (server-specific)
def init_db():
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    
    # Bot configs table
    c.execute('''CREATE TABLE IF NOT EXISTS bot_configs
                 (id INTEGER PRIMARY KEY, token TEXT, guild_id TEXT, status TEXT, created_at TEXT)''')
    
    # Download links table
    c.execute('''CREATE TABLE IF NOT EXISTS download_links
                 (id INTEGER PRIMARY KEY, game TEXT, cheat TEXT, link1 TEXT, link2 TEXT, link3 TEXT, link4 TEXT)''')
    
    # Add default download links
    default_links = [
        ('fortnite', 'arly-cracked', 'https://mega.nz/arly-fn', 'https://drive.google.com/arly', 'https://mediafire.com/arly', 'https://t.me/mystic_arly'),
        ('fortnite', 'softhub-free', 'https://mega.nz/softhub-fn', 'https://drive.google.com/softhub', 'https://mediafire.com/softhub', 'https://t.me/mystic_softhub'),
        ('fortnite', 'mystware-premium', 'https://mega.nz/mystware', 'https://drive.google.com/mystware', 'https://mediafire.com/mystware', 'https://t.me/mystic_mystware'),
        ('valorant', 'phantom-overlay', 'https://mega.nz/phantom-val', 'https://drive.google.com/phantom', 'https://mediafire.com/phantom', 'https://t.me/mystic_phantom'),
        ('valorant', 'viper-cheat', 'https://mega.nz/viper', 'https://drive.google.com/viper', 'https://mediafire.com/viper', 'https://t.me/mystic_viper'),
        ('valorant', 'mystic-val', 'https://mega.nz/mystic-val', 'https://drive.google.com/mystic-val', 'https://mediafire.com/mystic-val', 'https://t.me/mystic_val'),
        ('apex', 'apex-horizon', 'https://mega.nz/horizon', 'https://drive.google.com/horizon', 'https://mediafire.com/horizon', 'https://t.me/mystic_horizon'),
        ('apex', 'nighthawk-apex', 'https://mega.nz/nighthawk', 'https://drive.google.com/nighthawk', 'https://mediafire.com/nighthawk', 'https://t.me/mystic_nighthawk'),
        ('apex', 'mystic-apex', 'https://mega.nz/mystic-apex', 'https://drive.google.com/mystic-apex', 'https://mediafire.com/mystic-apex', 'https://t.me/mystic_apex'),
        ('cs2', 'osiris-cs2', 'https://mega.nz/osiris-cs2', 'https://drive.google.com/osiris', 'https://mediafire.com/osiris', 'https://t.me/mystic_osiris'),
        ('cs2', 'gamesense-cs2', 'https://mega.nz/gamesense', 'https://drive.google.com/gamesense', 'https://mediafire.com/gamesense', 'https://t.me/mystic_gamesense'),
        ('cs2', 'mystic-cs2', 'https://mega.nz/mystic-cs2', 'https://drive.google.com/mystic-cs2', 'https://mediafire.com/mystic-cs2', 'https://t.me/mystic_cs2'),
        ('cod', 'warzone-plus', 'https://mega.nz/warzone', 'https://drive.google.com/warzone', 'https://mediafire.com/warzone', 'https://t.me/mystic_warzone'),
        ('cod', 'cod-engine', 'https://mega.nz/cod-engine', 'https://drive.google.com/cod-engine', 'https://mediafire.com/cod-engine', 'https://t.me/mystic_cod'),
        ('cod', 'mystic-cod', 'https://mega.nz/mystic-cod', 'https://drive.google.com/mystic-cod', 'https://mediafire.com/mystic-cod', 'https://t.me/mystic_cod_pro'),
    ]
    
    for link in default_links:
        c.execute('INSERT OR IGNORE INTO download_links (game, cheat, link1, link2, link3, link4) VALUES (?, ?, ?, ?, ?, ?)', link)
    
    conn.commit()
    conn.close()

class VerificationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="✅ Get Verified", style=discord.ButtonStyle.green, emoji="✅")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            verified_role = discord.utils.get(interaction.guild.roles, name="🆓 Verified")
            unverified_role = discord.utils.get(interaction.guild.roles, name="❌ Unverified")
            
            if verified_role and unverified_role:
                await interaction.user.remove_roles(unverified_role)
                await interaction.user.add_roles(verified_role)
                
                embed = discord.Embed(
                    title="✅ Successfully Verified!",
                    description=f"Welcome to **Mystic Gaming**, {interaction.user.mention}!\n\n🎮 You now have access to all free cheats and tools!",
                    color=0x00FF00
                )
                
                embed.add_field(
                    name="🔓 What's Unlocked:",
                    value="• All game download channels\n• Free cheat downloads\n• View announcements and updates\n• Premium upgrade available",
                    inline=False
                )
                
                embed.add_field(
                    name="💎 Want Premium?",
                    value="Contact staff to upgrade for exclusive premium cheats!",
                    inline=False
                )
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message("❌ Verification roles not found. Contact staff!", ephemeral=True)
                
        except Exception as e:
            await interaction.response.send_message("❌ Verification failed. Contact staff for help.", ephemeral=True)

@bot.event
async def on_ready():
    print(f'🔥 {bot.user} is online and ready!')
    print(f'🎮 Mystic Gaming Bot - Server ID: {SERVER_ID}')
    print(f'🏭 Guild ID: {GUILD_ID}')
    print(f'📊 Connected to {len(bot.guilds)} servers')
    print(f'📋 Database: {db_name}')
    
    # Add persistent view
    bot.add_view(VerificationView())
    
    # Auto-setup server if GUILD_ID is specified
    if GUILD_ID:
        guild = bot.get_guild(int(GUILD_ID))
        if guild:
            print(f'🎯 Target server: {guild.name}')
            # Auto-create channels if needed
            await auto_setup_server(guild)

@bot.event
async def on_member_join(member):
    """Auto-assign unverified role to new members"""
    unverified_role = discord.utils.get(member.guild.roles, name="❌ Unverified")
    if unverified_role:
        await member.add_roles(unverified_role)

@bot.command(name='help')
async def help_command(ctx):
    """Enhanced help command"""
    embed = discord.Embed(
        title="🔥 Mystic Gaming Bot Commands",
        description="**The Ultimate Gaming Enhancement Bot**",
        color=0xFF0000
    )
    
    embed.add_field(
        name="🎮 User Commands",
        value="`!help` - Show this help menu\n`!status` - Check bot status\n`!games` - List all supported games\n`!verify` - Get verification link",
        inline=False
    )
    
    embed.add_field(
        name="🛠️ Admin Commands",
        value="`!setup` - Setup server (Admin only)\n`!links <game>` - View download links\n`!updatelink` - Update download links",
        inline=False
    )
    
    embed.add_field(
        name="💎 Premium Features",
        value="• Exclusive premium cheats\n• Priority support\n• Early access to new tools\n• Custom configurations",
        inline=False
    )
    
    embed.set_footer(text="Mystic Gaming • The #1 Choice for Gamers")
    await ctx.send(embed=embed)

@bot.command(name='games')
async def games_command(ctx):
    """List all supported games"""
    embed = discord.Embed(
        title="🎮 Supported Games",
        description="**All games with available cheats and tools**",
        color=0x00FF00
    )
    
    games_list = [
        "🛡️ **Fortnite** - Arly, SoftHub, MystWare",
        "⚡ **Valorant** - Phantom, Viper, Mystic Pro",
        "🔫 **Apex Legends** - Horizon, NightHawk, Mystic Pro", 
        "🔥 **CS2** - Osiris, GameSense, Mystic Pro",
        "💥 **COD Warzone** - WarzonePlus, COD Engine, Mystic Pro"
    ]
    
    embed.add_field(
        name="Available Games:",
        value="\n".join(games_list),
        inline=False
    )
    
    embed.add_field(
        name="📥 How to Download:",
        value="Go to the respective game channels and click the download buttons!",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name='status')
async def status_command(ctx):
    """Bot status command"""
    embed = discord.Embed(
        title="📊 Mystic Bot Status",
        color=0x00FF00
    )
    
    embed.add_field(name="🟢 Status", value="Online & Active", inline=True)
    embed.add_field(name="🎮 Servers", value=len(bot.guilds), inline=True)
    embed.add_field(name="👥 Users", value=sum(guild.member_count for guild in bot.guilds), inline=True)
    embed.add_field(name="⚡ Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="🕐 Uptime", value="24/7 Online", inline=True)
    embed.add_field(name="🔄 Last Update", value="Today", inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='setup')
@commands.has_permissions(administrator=True)
async def setup_server(ctx):
    """Setup the server with roles and channels"""
    try:
        # Setup roles
        roles_data = [
            ("❌ Unverified", discord.Color.red()),
            ("🆓 Verified", discord.Color.green()),
            ("💎 Premium", discord.Color.purple())
        ]
        
        created_roles = {}
        for role_name, color in roles_data:
            existing_role = discord.utils.get(ctx.guild.roles, name=role_name)
            if not existing_role:
                role = await ctx.guild.create_role(name=role_name, color=color)
                created_roles[role_name] = role
            else:
                created_roles[role_name] = existing_role
        
        # Create verification category and channel
        verify_category = discord.utils.get(ctx.guild.categories, name="✅ VERIFICATION")
        if not verify_category:
            verify_category = await ctx.guild.create_category("✅ VERIFICATION")
        
        verify_channel = discord.utils.get(verify_category.channels, name="verify-here")
        if not verify_channel:
            verify_channel = await ctx.guild.create_text_channel("verify-here", category=verify_category)
            
            # Set permissions
            await verify_channel.set_permissions(ctx.guild.default_role, view_channel=False)
            await verify_channel.set_permissions(created_roles["❌ Unverified"], view_channel=True, send_messages=False)
            
            # Send verification embed
            embed = discord.Embed(
                title="✅ VERIFICATION REQUIRED",
                description="**Welcome to Mystic Gaming!**\n\nClick the button below to get verified and access all free cheats!",
                color=0x00FF00
            )
            
            embed.add_field(
                name="🎮 What You'll Get:",
                value="• Access to all download channels\n• Free cheat downloads\n• View announcements\n• Premium upgrade options",
                inline=False
            )
            
            view = VerificationView()
            await verify_channel.send(embed=embed, view=view)
        
        embed = discord.Embed(
            title="✅ Server Setup Complete!",
            description="Verification system and roles have been configured.",
            color=0x00FF00
        )
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Setup failed: {str(e)}")

def get_download_links(game, cheat):
    """Get download links from database"""
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('SELECT link1, link2, link3, link4 FROM download_links WHERE game=? AND cheat=?', (game, cheat))
    result = c.fetchone()
    conn.close()
    return result if result else (None, None, None, None)

@bot.command(name='download')
async def download_command(ctx, game=None):
    """Enhanced download command with setup instructions"""
    if not game:
        embed = discord.Embed(
            title="🎮 Available Games",
            description="Use `!download <game>` to get download links and setup instructions",
            color=0x00FF00
        )
        embed.add_field(
            name="📋 Supported Games:",
            value="• `fortnite` - Multiple cheat options\n• `valorant` - Premium overlays\n• `cs2` - Advanced cheats\n• `apex` - Horizon & NightHawk\n• `cod` - Warzone tools",
            inline=False
        )
        await ctx.send(embed=embed)
        return
    
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('SELECT cheat, link1, link2, link3, link4 FROM download_links WHERE game=?', (game.lower(),))
    results = c.fetchall()
    conn.close()
    
    if not results:
        await ctx.send(f"❌ No cheats found for game: {game}")
        return
    
    # Setup instructions embed
    setup_embed = discord.Embed(
        title=f"🎯 {game.upper()} Setup Guide",
        description="**Follow these steps exactly for successful injection:**",
        color=0xFF6B35
    )
    
    setup_steps = [
        "1️⃣ **Download**: Choose any link below to get `{}-cheat.rar`".format(game),
        "2️⃣ **Extract**: Use password `mystic25` to extract files",
        "3️⃣ **Launch**: Run `main.bat` (our injection bypasser)",
        "4️⃣ **Warning**: May flag as false positive - this is normal",
        "5️⃣ **Detection**: Wait for automatic game detection",
        "6️⃣ **Injection**: Our custom system injects automatically",
        "7️⃣ **Activate**: In lobby, press `INSERT` or `F12`",
        "8️⃣ **Support**: Contact owners if you need help!"
    ]
    
    setup_embed.add_field(
        name="📝 Setup Instructions:",
        value="\n".join(setup_steps),
        inline=False
    )
    
    setup_embed.add_field(
        name="🔐 Extract Password:",
        value="`mystic25`",
        inline=True
    )
    
    setup_embed.add_field(
        name="🎮 Activation Keys:",
        value="`INSERT` or `F12`",
        inline=True
    )
    
    await ctx.send(embed=setup_embed)
    
    # Download links embed
    links_embed = discord.Embed(
        title=f"📥 {game.upper()} Download Links",
        description="**Choose any download source below:**",
        color=0x00FF00
    )
    
    for cheat, link1, link2, link3, link4 in results:
        cheat_name = cheat.replace('-', ' ').title()
        links_text = f"🔗 [Mega.nz]({link1})\n🔗 [Google Drive]({link2})\n🔗 [MediaFire]({link3})\n🔗 [Telegram]({link4})"
        links_embed.add_field(name=f"**{cheat_name}**", value=links_text, inline=False)
    
    links_embed.set_footer(text="Password: mystic25 | Support: Contact owners for help")
    await ctx.send(embed=links_embed)

@bot.command(name='links')
async def view_links(ctx, game=None):
    """Legacy command - redirects to download command"""
    await download_command(ctx, game)

# Auto-setup server function
async def auto_setup_server(guild):
    """Automatically setup server with basic channels and roles"""
    try:
        print(f'🚀 Auto-setting up server: {guild.name}')
        
        # Create basic roles if they don't exist
        roles_to_create = [
            ("❌ Unverified", discord.Color.red()),
            ("🆓 Verified", discord.Color.green()),
            ("💸 Premium", discord.Color.purple())
        ]
        
        for role_name, color in roles_to_create:
            if not discord.utils.get(guild.roles, name=role_name):
                await guild.create_role(name=role_name, color=color)
                print(f'✅ Created role: {role_name}')
        
        # Create verification category and channel
        verify_category = discord.utils.get(guild.categories, name="✅ VERIFICATION")
        if not verify_category:
            verify_category = await guild.create_category("✅ VERIFICATION")
            
            # Create verify channel
            verify_channel = await guild.create_text_channel("verify-here", category=verify_category)
            
            # Set permissions
            unverified_role = discord.utils.get(guild.roles, name="❌ Unverified")
            if unverified_role:
                await verify_channel.set_permissions(guild.default_role, view_channel=False)
                await verify_channel.set_permissions(unverified_role, view_channel=True, send_messages=False)
            
            # Send verification embed
            embed = discord.Embed(
                title="✅ VERIFICATION REQUIRED",
                description="**Welcome to Mystic Gaming!**\n\nClick the button below to get verified and access all free cheats!",
                color=0x00FF00
            )
            
            embed.add_field(
                name="🎮 What You'll Get:",
                value="• Access to all download channels\n• Free cheat downloads\n• View announcements\n• Premium upgrade options",
                inline=False
            )
            
            view = VerificationView()
            await verify_channel.send(embed=embed, view=view)
            print('✅ Setup verification system')
        
        print(f'🎉 Server setup completed for {guild.name}!')
        
    except Exception as e:
        print(f'❌ Error during auto-setup: {e}')

# Message sending function for web interface
async def send_channel_message(channel_name: str, message: str, guild_id: Optional[str] = None) -> bool:
    """Send a message to a specific channel from web interface"""
    try:
        if guild_id:
            guild = bot.get_guild(int(guild_id))
        elif GUILD_ID:
            guild = bot.get_guild(int(GUILD_ID))
        else:
            guild = bot.guilds[0] if bot.guilds else None
            
        if not guild:
            return False
            
        channel = discord.utils.get(guild.text_channels, name=channel_name)
        if not channel:
            # Create channel if it doesn't exist
            channel = await guild.create_text_channel(channel_name)
            
        await channel.send(message)
        print(f'📤 Message sent to #{channel_name} in {guild.name}: {message[:50]}...')
        return True
    except Exception as e:
        print(f"Error sending message: {e}")
        return False

@bot.command(name='channel')
@commands.has_permissions(administrator=True)
async def create_game_channels(ctx):
    """Create all game-specific channels"""
    try:
        channels_to_create = [
            ("🎮 GAME DOWNLOADS", [
                ("fortnite", "🛡️ Fortnite cheats and tools"),
                ("valorant", "⚡ Valorant overlays and cheats"),
                ("cs2", "🔫 Counter-Strike 2 tools"),
                ("apex-legends", "💥 Apex Legends cheats"),
                ("cod-warzone", "🎯 Call of Duty tools")
            ]),
            ("📢 INFORMATION", [
                ("announcements", "📢 Server announcements"),
                ("setup-help", "❓ Get help with cheat setup"),
                ("general", "💬 General discussion")
            ])
        ]
        
        created = 0
        for category_name, channels in channels_to_create:
            # Create category
            category = discord.utils.get(ctx.guild.categories, name=category_name)
            if not category:
                category = await ctx.guild.create_category(category_name)
                
            # Create channels in category
            for channel_name, topic in channels:
                existing = discord.utils.get(category.channels, name=channel_name)
                if not existing:
                    await ctx.guild.create_text_channel(
                        channel_name, 
                        category=category,
                        topic=topic
                    )
                    created += 1
                    
        embed = discord.Embed(
            title="✅ Channels Created!",
            description=f"Successfully created {created} new channels.",
            color=0x00FF00
        )
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error creating channels: {str(e)}")

# Initialize database
init_db()

# Global bot instance for web interface
bot_instance = bot

# Run bot if token is provided
if __name__ == "__main__":
    if not BOT_TOKEN:
        print("❌ No bot token provided. Bot will be started via web interface.")
        sys.exit(1)
        
    if not GUILD_ID:
        print("⚠️ No guild ID provided. Bot will connect but won't auto-setup.")
    
    try:
        print(f"🚀 Starting Mystic Gaming Bot...")
        print(f"🔑 Server ID: {SERVER_ID}")
        print(f"🏭 Guild ID: {GUILD_ID or 'Not specified'}")
        print(f"📋 Database: {db_name}")
        print("🎮 Features: Auto-setup, Downloads, Custom messages, Multi-server support")
        
        # Initialize database
        init_db()
        
        bot.run(BOT_TOKEN)
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")
        sys.exit(1)
