import sys
from os.path import join, dirname
sys.path.append(join(dirname(__file__), '../..'))

from pokemon_ai.battle import Battle
from pokemon_ai.classes import Bag, Party, Player, Move, MoveBank, Pokemon, Stats, PokemonType


party1 = Party([
    Pokemon(PokemonType.FIRE, "Charizard", 100, Stats(300, 300, 300, 300, 300), MoveBank([
        Move("Flamethrower", 100, 0, PokemonType.FIRE, True)
    ]), 300),
    Pokemon(PokemonType.WATER, "Piplup", 100, Stats(300, 300, 300, 300, 300), MoveBank([
        Move("Water Squirt", 100, 3, PokemonType.WATER, True)
    ]), 300)
])
party2 = Party([
    Pokemon(PokemonType.FIRE, "Blaziken", 100, Stats(300, 300, 300, 300, 300), MoveBank([
        Move("Flamethrower", 100, 3, PokemonType.FIRE, True)
    ]), 300),
    Pokemon(PokemonType.WATER, "Squirtle", 100, Stats(300, 300, 300, 300, 300), MoveBank([
        Move("Water Squirt", 100, 3, PokemonType.WATER, True)
    ]), 300)
])

player1 = Player("Player 1", party1, Bag())
player2 = Player("Player 2", party2, Bag())

battle = Battle(player1, player2, 2)
battle.play()
