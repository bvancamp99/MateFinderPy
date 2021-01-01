# ChessPlayer

working on heuristic function, more notes in post-optimization2 folder as well as mention of a bug

maybe store all max_depth last_moves for each part of the search tree rather than just one
- then you can evaluate useless moves a little better, e.g. random move but unrelated move 2 moves later is good so good hurr durr

punish moves that just end up obstructing the moving piece
- could check if the piece's move generator yields at least a few pieces

try to somehow account for the horizon effect
- it's particularly a problem when there's a big reward right at max_depth but the very next move shits on it
- maybe a potentially big reward could check if pieces are nearby to verify
- or if the same move could have been made earlier but wasn't, then it's probably not a good move
    - idk if can keep track of that with only prev_board and cur_board
    - maybe keep a list of board states for the current search

favor different things based on opening, midgame, and endgame sections

also have moves follow chess notation when printing them and accepting input
- also each whole move (turn) is two moves, not one

"Use the values as a guide, but use your own eyes as well."