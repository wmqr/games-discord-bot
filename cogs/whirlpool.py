import discord
from discord.ext import commands
from discord import app_commands
import random
from typing import Optional

class WhirlpoolGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games = {}  # Store active games
    
    def create_game_id(self, guild_id: int, channel_id: int) -> str:
        return f"{guild_id}_{channel_id}"

    @app_commands.command(name='whirlpool', description='Start a Whirlpool game')
    async def whirlpool(self, interaction: discord.Interaction):
        """Start a new Whirlpool game"""
        game_id = self.create_game_id(interaction.guild.id, interaction.channel.id)
        
        if game_id in self.games and self.games[game_id]['active']:
            await interaction.response.send_message('A game is already running in this channel!')
            return
        
        # Initialize game
        self.games[game_id] = {
            'active': True,
            'players': [interaction.user],
            'current_player_index': 0,
            'eliminated': [],
            'round': 1
        }
        
        embed = discord.Embed(
            title='🌀 Whirlpool Game Started!',
            description=f'{interaction.user.mention} has started a Whirlpool game!\n\nUse `/whirlpool_join` to join the game.',
            color=discord.Color.blue()
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='whirlpool_join', description='Join an active Whirlpool game')
    async def whirlpool_join(self, interaction: discord.Interaction):
        """Join an active Whirlpool game"""
        game_id = self.create_game_id(interaction.guild.id, interaction.channel.id)
        
        if game_id not in self.games or not self.games[game_id]['active']:
            await interaction.response.send_message('No active game in this channel. Use `/whirlpool` to start one!')
            return
        
        game = self.games[game_id]
        
        if interaction.user in game['players']:
            await interaction.response.send_message('You are already in this game!')
            return
        
        game['players'].append(interaction.user)
        
        embed = discord.Embed(
            title='🌀 Player Joined!',
            description=f'{interaction.user.mention} joined the game!\n\n**Players ({len(game["players"])}):**\n' + 
                       '\n'.join([f'{i+1}. {p.mention}' for i, p in enumerate(game['players'])]),
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='whirlpool_start', description='Start the Whirlpool game')
    async def whirlpool_start(self, interaction: discord.Interaction):
        """Start the Whirlpool game (must have at least 2 players)"""
        game_id = self.create_game_id(interaction.guild.id, interaction.channel.id)
        
        if game_id not in self.games or not self.games[game_id]['active']:
            await interaction.response.send_message('No active game in this channel!')
            return
        
        game = self.games[game_id]
        
        if len(game['players']) < 2:
            await interaction.response.send_message('Need at least 2 players to start!')
            return
        
        # Randomize player order
        random.shuffle(game['players'])
        game['current_player_index'] = 0
        
        current_player = game['players'][game['current_player_index']]
        
        embed = discord.Embed(
            title='🌀 Whirlpool Game Started!',
            description=f'**Round {game["round"]}**\n\n{current_player.mention} is the current player!\n\nChoose a player to eliminate using `/whirlpool_choose @player`',
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name='Players Alive',
            value='\n'.join([f'{i+1}. {p.mention}' for i, p in enumerate(game['players'])]),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='whirlpool_choose', description='Choose a player to eliminate')
    async def whirlpool_choose(self, interaction: discord.Interaction, target: discord.User):
        """Choose a player to eliminate in Whirlpool"""
        game_id = self.create_game_id(interaction.guild.id, interaction.channel.id)
        
        if game_id not in self.games or not self.games[game_id]['active']:
            await interaction.response.send_message('No active game in this channel!')
            return
        
        game = self.games[game_id]
        current_player = game['players'][game['current_player_index']]
        
        if interaction.user != current_player:
            await interaction.response.send_message(f'It\'s {current_player.mention}\'s turn, not yours!')
            return
        
        if target not in game['players']:
            await interaction.response.send_message('That player is not in the game!')
            return
        
        if target in game['eliminated']:
            await interaction.response.send_message('That player is already eliminated!')
            return
        
        if target == interaction.user:
            await interaction.response.send_message('You cannot choose yourself!')
            return
        
        # Eliminate the chosen player
        game['players'].remove(target)
        game['eliminated'].append(target)
        
        embed = discord.Embed(
            title='💀 Player Eliminated!',
            description=f'{target.mention} has been eliminated by {current_player.mention}!',
            color=discord.Color.red()
        )
        
        # Check if game is over
        if len(game['players']) == 1:
            winner = game['players'][0]
            embed.title = '🎉 Game Over!'
            embed.description = f'{winner.mention} is the last player standing and wins the game!'
            embed.color = discord.Color.gold()
            game['active'] = False
            
            await interaction.response.send_message(embed=embed)
            return
        
        # Move to next player
        game['current_player_index'] = (game['current_player_index'] + 1) % len(game['players'])
        next_player = game['players'][game['current_player_index']]
        
        alive_count = len(game['players'])
        
        embed2 = discord.Embed(
            title='🌀 Next Turn!',
            description=f'{next_player.mention}, it\'s your turn!\n\nChoose a player to eliminate using `/whirlpool_choose @player`',
            color=discord.Color.blue()
        )
        
        embed2.add_field(
            name=f'Players Alive ({alive_count})',
            value='\n'.join([f'{i+1}. {p.mention}' for i, p in enumerate(game['players'])]),
            inline=False
        )
        
        embed2.add_field(
            name='Eliminated',
            value='\n'.join([f'- {p.mention}' for p in game['eliminated']]),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
        await interaction.followup.send(embed=embed2)

    @app_commands.command(name='whirlpool_status', description='Check current game status')
    async def whirlpool_status(self, interaction: discord.Interaction):
        """Check the status of the current Whirlpool game"""
        game_id = self.create_game_id(interaction.guild.id, interaction.channel.id)
        
        if game_id not in self.games or not self.games[game_id]['active']:
            await interaction.response.send_message('No active game in this channel!')
            return
        
        game = self.games[game_id]
        current_player = game['players'][game['current_player_index']]
        
        embed = discord.Embed(
            title='🌀 Whirlpool Game Status',
            description=f'**Round {game["round"]}**\n\nCurrent Player: {current_player.mention}',
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name=f'Players Alive ({len(game["players"])})',
            value='\n'.join([f'{i+1}. {p.mention}' for i, p in enumerate(game['players'])]),
            inline=False
        )
        
        if game['eliminated']:
            embed.add_field(
                name=f'Eliminated ({len(game["eliminated"])})',
                value='\n'.join([f'- {p.mention}' for p in game['eliminated']]),
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='whirlpool_end', description='End the current game')
    async def whirlpool_end(self, interaction: discord.Interaction):
        """End the current Whirlpool game"""
        game_id = self.create_game_id(interaction.guild.id, interaction.channel.id)
        
        if game_id not in self.games or not self.games[game_id]['active']:
            await interaction.response.send_message('No active game in this channel!')
            return
        
        game = self.games[game_id]
        game['active'] = False
        
        embed = discord.Embed(
            title='🌀 Game Ended',
            description='The Whirlpool game has been ended.',
            color=discord.Color.orange()
        )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(WhirlpoolGame(bot))
