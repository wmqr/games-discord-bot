import discord
from discord.ext import commands
from discord import app_commands
import random

class TriviaGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.trivia_questions = [
            {
                'question': 'What is the capital of France?',
                'options': ['Paris', 'London', 'Berlin', 'Madrid'],
                'correct': 0
            },
            {
                'question': 'What is the largest planet in our solar system?',
                'options': ['Saturn', 'Jupiter', 'Neptune', 'Uranus'],
                'correct': 1
            },
            {
                'question': 'Who wrote "Romeo and Juliet"?',
                'options': ['Mark Twain', 'William Shakespeare', 'Jane Austen', 'Charles Dickens'],
                'correct': 1
            },
            {
                'question': 'What is the smallest country in the world?',
                'options': ['Monaco', 'Vatican City', 'San Marino', 'Liechtenstein'],
                'correct': 1
            },
            {
                'question': 'What is the speed of light?',
                'options': ['300,000 km/s', '150,000 km/s', '450,000 km/s', '100,000 km/s'],
                'correct': 0
            },
            {
                'question': 'How many continents are there?',
                'options': ['5', '6', '7', '8'],
                'correct': 2
            },
            {
                'question': 'What is the chemical symbol for gold?',
                'options': ['Go', 'Gd', 'Au', 'Ag'],
                'correct': 2
            },
            {
                'question': 'Which country has the most population?',
                'options': ['India', 'United States', 'China', 'Indonesia'],
                'correct': 0
            },
        ]
        self.active_trivia = {}

    @app_commands.command(name='trivia', description='Play a trivia game')
    async def trivia(self, interaction: discord.Interaction):
        """Start a trivia question"""
        question_data = random.choice(self.trivia_questions)
        options = question_data['options']
        correct_idx = question_data['correct']
        
        embed = discord.Embed(
            title='🧠 Trivia Question',
            description=question_data['question'],
            color=discord.Color.purple()
        )
        
        for i, option in enumerate(options):
            emoji = '✅' if i == correct_idx else '❌'
            embed.add_field(name=f'{chr(65+i)}.', value=option, inline=False)
        
        embed.add_field(name='Choose an answer:', value='Use `/trivia_answer <A/B/C/D>`', inline=False)
        
        self.active_trivia[interaction.user.id] = {
            'correct': correct_idx,
            'options': options,
            'question': question_data['question']
        }
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='trivia_answer', description='Answer the trivia question')
    async def trivia_answer(self, interaction: discord.Interaction, answer: str):
        """Answer the current trivia question"""
        if interaction.user.id not in self.active_trivia:
            await interaction.response.send_message('No active trivia! Use `/trivia` to get a question.')
            return
        
        answer = answer.upper()
        if answer not in ['A', 'B', 'C', 'D']:
            await interaction.response.send_message('Please answer with A, B, C, or D')
            return
        
        trivia = self.active_trivia[interaction.user.id]
        answer_idx = ord(answer) - 65
        
        if answer_idx == trivia['correct']:
            embed = discord.Embed(
                title='✅ Correct!',
                description=f'The answer is: **{trivia["options"][trivia["correct"]]}**',
                color=discord.Color.gold()
            )
        else:
            embed = discord.Embed(
                title='❌ Wrong!',
                description=f'The correct answer is: **{trivia["options"][trivia["correct"]]}**\nYou answered: **{trivia["options"][answer_idx]}**',
                color=discord.Color.red()
            )
        
        del self.active_trivia[interaction.user.id]
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(TriviaGame(bot))
