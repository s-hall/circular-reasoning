# circular-reasoning

recreation of https://boardgamegeek.com/thread/1385646/complete-rules-circular-reasoning 
using pygame (pip3 install pygame) because it's sold out a lot... (rules there)

```
usage: python3 circoo.py <players> <keyboard_mode>
  players: 2, 3, or 4
  keyboard_mode:
    1: possible moves are shown, press the letter to move (recommended)
    0: they are not, click where you want to move, if it's legal it will move
```  

player order is in top middle

current player color is shown in middle

select a piece to move by pressing 2, 3, or 4 (corresponding to the piece), white dot indicates selected, do the move based on keyboard_mode

pieces return to corner with a black dot when they are completed

"u" to undo, can only undo within the round, might be a little buggy with keyboard_mode = 0

circoo.py is an object oriented refactoring of circ.py,
it has more features like undo and <keyboard_mode>
