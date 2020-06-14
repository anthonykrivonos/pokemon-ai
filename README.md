# 🔴 pokemon-ai

Pokémon battle simulator that uses reinforcement learning techniques to win against the opponent.

## Running

1. `git clone https://github.com/anthonykrivonos/pokemon-ai.git`
2. `cd pokemon-ai`
3. `pip3 install -r requirements.txt`
4. Run two player tests with `make two-player` or run the sample model with `make sample-model`.

## Creating a New Model

1. Duplicate `/src/ai/models/sample_model.py` in the same directory and rename it to anything of your choosing.
2. Suppose you named it `my_model.py`. Add the following to `/src/ai/models/__init__.py`:
    ```
    from .my_model import *
    ```
3. Code your model. Make sure only one of `attack`, `use_item`, or `switch_pokemon_at_idx` is called at the end of the turn.
4. Create a test file that mimics `/src/scripts/sample_model.py` and add it to the `Makefile`. Ensure one or both of the players you
are testing on has your model as its fourth argument. Note that your model should *not* be initialized. For example:
    ```
    my_player = Player("Jane Doe", my_party, my_bag, MyModel)
    ```


## Resources

[1] Sutton et. al., *Reinforcement Learning: An Introduction*, [http://incompleteideas.net/book/RLbook2020trimmed.pdf](http://incompleteideas.net/book/RLbook2020trimmed.pdf).