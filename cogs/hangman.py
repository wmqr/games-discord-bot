import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio

class HangmanGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.words = [
            'python', 'discord', 'programming', 'gaming', 'adventure', 'treasure',
            'mystery', 'puzzle', 'challenge', 'victory', 'champion', 'legendary',
            'dragon', 'wizard', 'castle', 'kingdom', 'magic', 'potion', 'sword'
        ]
        self.active_games = {}

    @app_commands.command(name='hangman', description='Play Hangman')
    async def hangman(self, interaction: discord.Interaction):
        """Start a Hangman game"""
        game_id = f"{interaction.user.id}_{interaction.channel.id}"
        
        word = random.choice(self.words)
        
        game_data = {
            'word': word,
            'guessed': set(),
            'wrong_guesses': set(),
            'max_wrong': 6,
            'user': interaction.user,
            'channel': interaction.channel
        }
        
        self.active_games[game_id] = game_data
        
        display = ' '.join(['_' if c not in game_data['guessed'] else c for c in word])
        
        embed = discord.Embed(
            title='🎮 Hangman Game',
            description=f'Guess the word!\n\n**Word:** {display}\n**Wrong Guesses:** 0/{game_data["max_wrong"]}',
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed)
        await interaction.followup.send(f'{interaction.user.mention}, reply with a letter to guess!')

    @app_commands.command(name='guess', description='Guess a letter in Hangman')
    async def guess(self, interaction: discord.Interaction, letter: str):
        """Guess a letter in the active Hangman game"""
        game_id = f"{interaction.user.id}_{interaction.channel.id}"
        
        if game_id not in self.active_games:
            await interaction.response.send_message('No active Hangman game! Use `/hangman` to start.')
            return
        
        game = self.active_games[game_id]
        
        if interaction.user != game['user']:
            await interaction.response.send_message('This is not your game!')
            return
        
        letter = letter.lower()
        
        if len(letter) != 1 or not letter.isalpha():
            await interaction.response.send_message('Please guess a single letter!')
            return
        
        if letter in game['guessed'] or letter in game['wrong_guesses']:
            await interaction.response.send_message(f'You already guessed "{letter}"!')
            return
        
        word = game['word']
        
        if letter in word:
            game['guessed'].add(letter)
            result = f'✅ Correct! "{letter}" is in the word.'
        else:
            game['wrong_guesses'].add(letter)
            result = f'❌ Wrong! "{letter}" is not in the word.'
        
        # Display word
        display = ' '.join(['_' if c not in game['guessed'] else c for c in word])
        
        # Check if won
        if all(c in game['guessed'] for c in word):
            embed = discord.Embed(
                title='🎉 You Won!',
                description=f'The word was: **{word}**',
                color=discord.Color.gold()
            )
            del self.active_games[game_id]
            await interaction.response.send_message(result)
            await interaction.followup.send(embed=embed)
            return
        
        # Check if lost
        if len(game['wrong_guesses']) >= game['max_wrong']:
            embed = discord.Embed(
                title='💀 Game Over!',
                description=f'You lost! The word was: **{word}**',
                color=discord.Color.red()
            )
            del self.active_games[game_id]
            await interaction.response.send_message(result)
            await interaction.followup.send(embed=embed)
            return
        
        embed = discord.Embed(
            title='🎮 Hangman Game',
            description=f'{result}\n\n**Word:** {display}\n**Wrong Guesses:** {len(game["wrong_guesses"])}/{game["max_wrong"]}\n**Guessed Letters:** {", ".join(sorted(game["guessed"] | game["wrong_guesses"]))}',
            color=discord.Color.blue()
        )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(HangmanGame(bot))
