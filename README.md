# ChessPlayer

## TODO
Performance:
getKing optimize (currently O(N^2)), store black and white king location in board state
Alternative for arePiecesBetween method? store that info somewhere?
Figure out why i copy default objects instead of creating new ones
If ai sees checkmate, save those moves, no need to recalculate them
Give ai some opening moves so it isn't essentially rando-picking the first move
- Could incentise developing toward the centre?
Incentivise trades only if up in material
Dynamic piece values
- Based on how strong they are in a given position
- Could be as simple as how many unobstructed moves they can make or pieces they can take or smth

Visual:
Correct chess notation
AI vs AI game mode (easier to test)


Organisation:
Revisit ICON_SET (needed or just assume char is fine in chessGame line ~106?)
Split up chessGame into multiple files
Tab = 4 spaces -> tab = 2 spaces
GetChessPosition and isCastleEligible are unused, remove?
Change implementation of ChessBoard to not require board parameter?
- It should just be the object itself, you can create board copies for hypothetical board states and call their methods
description for each file
- Might be like this so the other classes have access to the same board?
- Maybe separate into two classes, one for board logic and the other for board state
x -> pos ou qch d'autre, pieceObj


