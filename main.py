import os
from typing import Final, Dict
from dotenv import load_dotenv
from discord.ext import commands
from discord import Intents
import discord
import random
import asyncio

load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

# Intents configuration and bot creation
intents = Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='r!', intents=intents, help_command=None)



# ========== Casino cfg/func ===========
# Initialize the economy system (in-memory storage for simplicity)
economy: Dict[int, int] = {}

def draw_card(): # Blackjack func
    return random.choice(list(card_values.keys()))

def calculate_hand(hand): # Blackjack func
    total = sum(card_values[card] for card in hand)
    aces = hand.count('A')

    while total > 21 and aces:
        total -= 10
        aces -= 1

    return total

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

# Blackjack cards configuration
card_values = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 10, 'Q': 10, 'K': 10, 'A': 11
}


# ============ Commands ============
@client.command(name='help')
async def help(ctx):
    help_message = discord.Embed(
        title='CasinoHUB by Lostdou || r!help',
        description=(
            '**Comandos Disponibles:**\n'
            '1- `r!balance`: Mira cuánto dinero tienes\n'
            '2- `r!addmoney @usuario (cantidad)`: Añade dinero a un usuario específico (requiere administrador)\n'
            '3- `r!removemoney @usuario (cantidad)`: Quita dinero a un usuario específico (requiere administrador)\n'
            '4- `r!ruleta (apuesta) (color/número)`: Juega a la ruleta\n'
            '5- `r!blackjack (apuesta)`: Juega al blackjack\n'
            '6- `r!help`: Muestra este mensaje'
        ),
        color=discord.Color.blue()
    )
    await ctx.send(embed=help_message)

@client.command(name='balance')
async def balance(ctx, member: discord.Member = None):
    """Check the balance of a user."""
    member = member or ctx.author
    balance = economy.get(member.id, 1000)  # Get the user's balance, default to 1000
    
    embed = discord.Embed(
        title="Balance de monedas",
        description=f'{member.display_name} tiene {balance} monedas.',
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@client.command(name='addmoney')
@commands.has_permissions(administrator=True)
async def add_money(ctx, member: discord.Member, amount: int):
    """Add money to a user's balance."""
    if amount < 0:
        embed = discord.Embed(
            title="Error",
            description='No puedes agregar una cantidad negativa.',
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    economy[member.id] = economy.get(member.id, 1000) + amount
    embed = discord.Embed(
        title="Monedas añadidas",
        description=f'Añadido {amount} monedas a {member.display_name}. Balance actual: {economy[member.id]}',
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

@client.command(name='removemoney')
@commands.has_permissions(administrator=True)
async def remove_money(ctx, member: discord.Member, amount: int):
    """Remove money from a user's balance."""
    if amount < 0:
        embed = discord.Embed(
            title="Error",
            description='No puedes sustraer una cantidad negativa.',
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    economy[member.id] = economy.get(member.id, 1000) - amount
    embed = discord.Embed(
        title="Monedas sustraídas",
        description=f'Sustraído {amount} monedas a {member.display_name}. Balance actual: {economy[member.id]}',
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)


# ============ Casino ===================
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

    embed=discord.Embed(title=f'Ruleta de {ctx.author.display_name}', description=f'La ruleta giró y salió el número **{resultado_numero}** de color **{resultado_color}**.\n **{resultado}** Ahora tienes {economy[ctx.author.id]} monedas.')
    embed.set_image(url='https://www.gifss.com/economia/juego/images/ruleta-05.gif')
    await ctx.send(embed=embed)

@client.command(name='blackjack')
async def blackjack(ctx, apuesta: int):
    """Play a game of blackjack."""
    if apuesta <= 0:
        await ctx.send('La apuesta debe ser mayor que 0.')
        return

    if economy.get(ctx.author.id, 1000) < apuesta:
        await ctx.send('No tienes suficientes monedas para hacer esa apuesta.')
        return

    player_hand = [draw_card(), draw_card()]
    dealer_hand = [draw_card(), draw_card()]

    player_score = calculate_hand(player_hand)
    dealer_score = calculate_hand(dealer_hand)

    embed = discord.Embed(
        title=f"Blackjack de {ctx.author.display_name}",
        description=f'Tu mano: {", ".join(player_hand)} (Total: {player_score})\n'
                    f'Mano del dealer: {dealer_hand[0]}, ?',
        color=discord.Color.gold()
    )
    await ctx.send(embed=embed)

    def check(message):
        return message.author == ctx.author and message.content.lower() in ['quedarse', 'pedir']

    while player_score < 21:
        embed = discord.Embed(
            title="¿Te quedas o pides otra carta?",
            description="Responde con 'quedarse' o 'pedir'.",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)

        try:
            response = await client.wait_for('message', check=check, timeout=30.0)
        except asyncio.TimeoutError:
            embed = discord.Embed(
                title="Tiempo agotado",
                description="Te has tardado demasiado en responder. El juego ha terminado.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if response.content.lower() == 'pedir':
            player_hand.append(draw_card())
            player_score = calculate_hand(player_hand)
            embed = discord.Embed(
                title="Nueva carta",
                description=f'Nueva carta: {player_hand[-1]}. Tu mano: {", ".join(player_hand)} (Total: {player_score})',
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        else:
            break

    if player_score > 21:
        embed = discord.Embed(
            title="Te pasaste",
            description=f'Te pasaste de 21. ¡Perdiste! Has perdido {apuesta} monedas.',
            color=discord.Color.red()
        )
        economy[ctx.author.id] -= apuesta
    else:
        while dealer_score < 17:
            dealer_hand.append(draw_card())
            dealer_score = calculate_hand(dealer_hand)

        embed = discord.Embed(
            title=f"Resultado del Blackjack de {ctx.author.display_name}",
            description=f'Tu mano: {", ".join(player_hand)} (Total: {player_score})\n'
                        f'Mano del dealer: {", ".join(dealer_hand)} (Total: {dealer_score})',
            color=discord.Color.gold()
        )

        if dealer_score > 21 or player_score > dealer_score:
            embed.add_field(name="Resultado", value=f'¡Ganaste! Has ganado {apuesta} monedas.')
            economy[ctx.author.id] += apuesta
        elif player_score < dealer_score:
            embed.add_field(name="Resultado", value=f'Perdiste. Has perdido {apuesta} monedas.')
            economy[ctx.author.id] -= apuesta
        else:
            embed.add_field(name="Resultado", value='Empate. Tu apuesta ha sido devuelta.')

    await ctx.send(embed=embed)


# ============ Events ==============
# Event triggered when the bot is ready
@client.event
async def on_ready():
    print(f'{client.user.name} está listo! / {client.user.name} is ready!')
    await client.change_presence(activity=discord.Game(name="r!help"))

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
