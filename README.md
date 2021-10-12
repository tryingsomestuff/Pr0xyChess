# Pr0xyChess
A proxy for multi-engine chess game

# How to use it

Use it as a "proxy" UCI chess engine in your tournament manager (it works in cutechess at least ...)
using this kind of `command` :
```
python3 ./Pr0xyChess.py -n 5 -e /ssd/Minic/Tourney/minic_dev_linux_x64 /ssd/engines/Weiss/src/weiss
```
You can add any number engine you want and configure the number of consecutive moves for each engine using the `-n` option.

![image](https://user-images.githubusercontent.com/5878710/136948147-5b35930f-530a-48bb-b1ca-f8a2ab7f9f02.png)
