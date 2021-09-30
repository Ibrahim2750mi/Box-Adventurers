# Box Adventures
Its a game which does infinite terrain generation, the player has no specific objective in the game you can try reaching the world border.



# Features:

+ block breaking

+ loadable chunks

+ terrain generation

+ 4 biomes



# Contributions

+ BeautifulReques: Terrain generation, optimisation, graphics, chunk class

+ aph: graphics, block class

+ redish2098: music, item class

+ Vthechamp: bug fixing and re-assesing the code

+ SReaperz: block breaking, player class, inventory, camera, entity class

+ jack_sparrow: start screen



# BUGS

+ While in unloading chunks it gives error leading the game to crashing, reason when we break a block it doesn't removes the block from the loaded chunk in the list, didn't had time to solve this. Also a physical fix is that increasing the `VISIBLE_RANGE_MAX` and `VISIBLE_RANGE_MIN` in config.py| (SOLVED)



# How to Run

after installing the libs in `requirments.txt` do `python src/game.py`
