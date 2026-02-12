# ChessPlayer


## TODO: working on chess_board
LINE 139 FIX pieceTYPE= not s=

Performance:
Is it possible to not need to copy board state?
- Reverse move after recursion call in minimax to restore current board state?
- Single set of piece positions that also is not copied but instead reverse updated after minimax call?
- King position list would also need to be reverse updated
- Would need a reverse_move method in ChessBoard class, think about parameters required
Optimise ChessBoard.getKing and ChessBoard.yieldPieces
- store positions instead of piece objects!
getKing optimise (currently O(N^2)), store black and white king location in board state
Optimise yieldPieces, store in a data structure for each board?
- would also optimise getKing
- would have to replace piece objects from data structure every time a movement on the board is made
Alternative for arePiecesBetween method? store that info somewhere?
If ai sees checkmate, save those moves, no need to recalculate them
yield_pieces and yield_std_moves has unused piece_type paramter, if I don't include that I could have piece_pos be a tuple of sets representing black and white positions
would_put_king_in_check could I check this without having to move and/or check all opponent moves?
King._yield_open_pos Don't we need to check if king would land too close to opponent king?
- maybe add that check in an overridden King.yield_std_moves?
Verify the methods that should be yield vs returning e.g. a list
- return is faster unless you don't need all iterations completed


Heuristic:
https://youtu.be/3su1RGtmfcw How to evaluate a chess position
Maybe heuristic could just be result of evaluating the chess position?
- that would probably require looking at the whole board
- for speed, it might be necessary to send previous pos eval as parameter if that helps
Give ai some opening moves so it isn't essentially rando-picking the first move
- Could incentise developing toward the centre?
Incentivise trades only if up in material
Dynamic piece values
- Based on how strong they are in a given position
- Could be as simple as how many unobstructed moves they can make or pieces they can take or smth
Currently the AI loves trading its well-developped pieces, this would probably be fixed by dynamic piece values.
- Might also have a tendancy to want to take pieces in basic heuristic, improve that.
It likes to move rook B1 or G1 with typical 0.642 heuristic value.
- kind of a useless move, i would disincentivize moves that would prevent a future castle unless important
Give a little incentive for moves that open up the king to castle
It sacrificed a pawn for seemingly no reason, maybe to open up file for rook? Photo in discord me


Visual:
Correct chess notation
AI vs AI game mode (easier to test)
Custom game start templates
- black/white to move
Print which piece is moving


Organisation:
✅ standard template cells are (piece_type, colour) tuples instead of icons. Empty cells are just marked EMPTY.
Revisit ICON_SET (needed or just assume char is fine in chessGame line ~106?)
Split up chessGame into multiple files
isCastleEligible are unused, remove?
Change implementation of ChessBoard to not require board parameter?
- It should just be the object itself, you can create board copies for hypothetical board states and call their methods
description for each file
- Might be like this so the other classes have access to the same board?
- Maybe separate into two classes, one for board logic (in const.py) and the other for board state (many instances)
- board logic has the methods and iconToObject, board states have the dynamic data structures
x -> pos ou qch d'autre, pieceObj
return to snake_case
chess_piece.py
does each chess piece need a reference to board object?
figure out why king needs a different isunderattack method
- I figured out why! It checks everything except if the potential opponent move would put the opponent's king in check because, even though that would prevent it from making the move that would land on the king's position, it's still a check. You don't need to land on the king to check it, you just need to have an unobstructed end position that is equal to the king's position.
Use None instead of an EMPTY const variable?
Rewrite ChessBoard class in new chess_board.py file
Rename en_passant and castle to move_en_passant and move_castle
make_move include wrappers for moving en_passant and castle so that the minimax just needs one call without if checks
- maybe a move could include an integer representing standard, en passant, or castle move
    - store as constant integers
    - minimax methods can have move_type integer instead of en_passant and castle boolean variables
- yield_moves same idea, maybe yield_all_moves method with yield_standard_moves, castle, en passant methods
Remove need for each ChessPiece method to have cur_board parameter, just use reference given in init method
Does ChessPiece.is_under_attack need to consider being attacked by a rook after a castle move?