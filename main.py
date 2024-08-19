import os
from typing import Final, Dict
from dotenv import load_dotenv
from discord.ext import commands
from discord import Intents
import discord
import random

load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

# Intents configuration and bot creation
intents = Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='r!', intents=intents, help_command=None)

# Initialize the economy system (in-memory storage for simplicity)
economy: Dict[int, int] = {}

# Standard roulette configuration
roulette_numbers = {
    0: 'verde',
    1: 'rojo', 2: 'negro', 3: 'rojo', 4: 'negro', 5: 'rojo', 6: 'negro',
    7: 'rojo', 8: 'negro', 9: 'rojo', 10: 'negro', 11: 'negro', 12: 'rojo',
    13: 'negro', 14: 'rojo', 15: 'negro', 16: 'rojo', 17: 'negro', 18: 'rojo',
    19: 'rojo', 20: 'negro', 21: 'rojo', 22: 'negro', 23: 'rojo', 24: 'negro',
    25: 'rojo', 26: 'negro', 27: 'rojo', 28: 'negro', 29: 'negro', 30: 'rojo',
    31: 'negro', 32: 'rojo', 33: 'negro', 34: 'rojo', 35: 'negro', 36: 'rojo'
}

# ============ Commands ============

@client.command(name='balance')
async def balance(ctx, member: discord.Member = None):
    """Check the balance of a user."""
    member = member or ctx.author
    balance = economy.get(member.id, 1000)  # Get the user's balance, default to 1000
    await ctx.send(f'{member.display_name} tiene {balance} monedas.')

@client.command(name='addmoney')
@commands.has_permissions(administrator=True)
async def add_money(ctx, member: discord.Member, amount: int):
    """Add money to a user's balance."""
    if amount < 0:
        await ctx.send('No puedes agregar una cantidad negativa.')
        return
    economy[member.id] = economy.get(member.id, 1000) + amount
    await ctx.send(f'Añadido {amount} monedas a {member.display_name}. Balance actual: {economy[member.id]}')

@client.command(name='removemoney')
@commands.has_permissions(administrator=True)
async def remove_money(ctx, member: discord.Member, amount: int):
    """Remove money from a user's balance."""
    if amount < 0:
        await ctx.send('No puedes sustraer una cantidad negativa.')
        return
    economy[member.id] = economy.get(member.id, 1000) - amount
    await ctx.send(f'Sustraído {amount} monedas a {member.display_name}. Balance actual: {economy[member.id]}')

@client.command(name='ruleta')
async def ruleta(ctx, apuesta: int, eleccion: str):
    """Play the roulette game."""
    if economy.get(ctx.author.id, 1000) < apuesta:
        await ctx.send('No tienes suficientes monedas para realizar esa apuesta.')
        return

    if eleccion.isdigit():
        eleccion = int(eleccion)
        if eleccion < 0 or eleccion > 36:
            await ctx.send('Número inválido. Debe estar entre 0 y 36.')
            return
        apuesta_tipo = 'numero'
    elif eleccion.lower() in ['rojo', 'negro', 'verde']:
        apuesta_tipo = 'color'
    else:
        await ctx.send('Elección inválida. Debe ser un número entre 0 y 36 o un color (rojo, negro, verde).')
        return

    # Generate random roulette outcome
    resultado_numero = random.randint(0, 36)
    resultado_color = roulette_numbers[resultado_numero]

    # Determine win or lose
    if apuesta_tipo == 'numero':
        if resultado_numero == eleccion:
            ganancia = apuesta * 2.0
            resultado = '¡Ganaste!'
        else:
            ganancia = -apuesta
            resultado = 'Perdiste.'
    elif apuesta_tipo == 'color':
        if resultado_color == eleccion.lower():
            if eleccion.lower() == 'verde':
                ganancia = apuesta * 2.5
            else:
                ganancia = apuesta * 1.5
            resultado = '¡Ganaste!'
        else:
            ganancia = -apuesta
            resultado = 'Perdiste.'

    # Update balance
    economy[ctx.author.id] = economy.get(ctx.author.id, 1000) + int(ganancia)

    await ctx.send(
        f'La ruleta giró y salió el número **{resultado_numero}** de color **{resultado_color}**.\n'
        f'{resultado} Ahora tienes {economy[ctx.author.id]} monedas.'
    )

# ============ Events ==============

# Event triggered when the bot is ready
@client.event
async def on_ready():
    print(f'{client.user.name} está listo! / {client.user.name} is ready!')
    await client.change_presence(activity=discord.Game(name=" r!randomize || https://github.com/Lostdou"))

# Event triggered when a member interacts with the bot for the first time
@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.author.id not in economy:
        economy[message.author.id] = 1000

    await client.process_commands(message)

# Run the bot
client.run(TOKEN)
