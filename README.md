# Box Adventures (PyWeek 34)

Its a game which does infinite terrain generation, the player has no
specific objective in the game you can try reaching the world border.

## Features:

* block breaking
* loadable chunks
* terrain generation
* 4 biomes

## Contributions

NHS (PyWeek Team)
* BeautifulReques (Ibrahim2750mi): terrain generation, optimisation, graphics, chunk system, re-write 2.0
* aph: graphics, block class
* redish2098: music, item class
* Vthechamp: bug fixing and re-assesing the code
* SReaperz: block breaking, player class, inventory, camera, entity class
* jack_sparrow: start screen

Arcade
* einarf: optimising, re-writing everything 1.0

## BUGS

* Currently inventory gets full without being full.

## How to Run

After installing the libs in `requirements.txt` do `python src/game.py`.
Currently, if there isn't game data present in data folder you have to run the game two times.

## Notes

* A block is 20 x 20 pixels
* Each HorizontalChunk is 16 x 320 blocks
