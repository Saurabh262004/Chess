from copy import copy
from math import floor
from classes import Piece

def pieceAt(pos, pieces):
  if pos[0] < 1 or pos[0] > 8 or pos[1] < 1 or pos[1] > 8:
    return None

  for piece in pieces:
    if (pos[0] == piece.pos[0]) and (pos[1] == piece.pos[1]):
      return piece
  return None

def toggle_var(var, var1, var2):
  if var == var1:
    return var2
  elif var == var2:
    return var1
  return var

def get_pieces(piece_col, piece_type, pieces):
  found_pieces = []
  for piece in pieces:
    if piece.col == piece_col and piece.type == piece_type:
      found_pieces.append(piece)
  return found_pieces

def is_square_safe(pos, from_col, pieces, match_history):
  for piece in pieces:
    if piece.col == from_col:
      distX = abs(piece.pos[0] - pos[0])
      distY = abs(piece.pos[1] - pos[1])
      if not ((piece.type == 'king') and (distX > 1 or distY > 1)):
        possible_piece_moves = get_moves_by_rule(piece, pieces, match_history)

        for move in possible_piece_moves:
          if pos[0] == move[0] and pos[1] == move[1]:
            return False

  return True

def straight_rule(move_piece, pieces):
  cPos = move_piece.pos
  moves = []

  for j in range(4):
    br = False
    brs = False

    if j == 0:
      a, b, c = cPos[1] - 1, 0, -1
    elif j == 1:
      a, b, c = cPos[0] + 1, 9, 1
    elif j == 2:
      a, b, c = cPos[1] + 1, 9, 1
    else:
      a, b, c = cPos[0] - 1, 0, -1

    for i in range(a, b, c):
      move = []

      if j == 0 or j == 2:
        move = [cPos[0], i]
      else:
        move = [i, cPos[1]]

      target = pieceAt(move, pieces)

      if target != None:
        if target.col == move_piece.col:
          br = True
        else:
          brs = True

      if br:
        br = False
        break
      if brs:
        brs = False
        br = True

      moves.append(move)
  return moves

def diagonal_rule(move_piece, pieces):
  cPos = move_piece.pos
  moves = []

  for j in range(4):
    br = False
    brs = False
    min_border_dist = 0

    if j == 0:
      min_border_dist = min(cPos)
    elif j == 1:
      min_border_dist = min([8-cPos[0], cPos[1]])+1
    elif j == 2:
      min_border_dist = min([8-cPos[0], 8-cPos[1]])+1
    else:
      min_border_dist = min([cPos[0], 8-cPos[1]])+1

    for i in range(1, min_border_dist):
      if j == 0:
        move = [cPos[0]-i, cPos[1]-i]
      elif j == 1:
        move = [cPos[0]+i, cPos[1]-i]
      elif j == 2:
        move = [cPos[0]+i, cPos[1]+i]
      else:
        move = [cPos[0]-i, cPos[1]+i]

      target = pieceAt(move, pieces)

      if target != None:
        if target.col == move_piece.col:
          br = True
        else:
          brs = True

      if br:
        br = False
        break
      if brs:
        brs = False
        br = True

      moves.append(move)

  return moves

def get_moves_by_rule(move_piece, pieces, match_history):
  available_moves = []
  cPos = move_piece.pos

  ## pawn ##
  ## please fix this if you have enough time ##
  if move_piece.type == 'pawn':
    ## en passant ##
    m_h_len = len(match_history)
    if (m_h_len > 0):
      last_move = match_history[m_h_len-1]
      last_move_previous = last_move[0]
      last_move_current = last_move[1]
      last_move_details = last_move[2]

      if (last_move_current[1] == move_piece.pos[1]) and (move_piece.pos[0]-2 < last_move_current[0] < move_piece.pos[0]+2) and (last_move_details[0] == 'pawn') and (not last_move_details[1] == move_piece.col) and (abs(last_move_previous[1] - last_move_current[1]) == 2):
        en_passant = [last_move_current[0], last_move_current[1]]
        if move_piece.col == 'white':
          en_passant[1] -= 1
        else:
          en_passant[1] += 1

        en_passant.append('enPassant')

        available_moves.append(en_passant)

    if move_piece.col == 'white':
      ## diagonal take ##
      diagonal_piece1 = pieceAt([cPos[0]-1, cPos[1]-1], pieces)
      diagonal_piece2 = pieceAt([cPos[0]+1, cPos[1]-1], pieces)
      if not diagonal_piece1 == None:
        if diagonal_piece1.col == 'black':
          available_moves.append(diagonal_piece1.pos)
      if not diagonal_piece2 == None:
        if diagonal_piece2.col == 'black':
          available_moves.append(diagonal_piece2.pos)

      ## check block ##
      if cPos[1] == 7:
        next_piece1 = pieceAt([cPos[0], 6], pieces)
        next_piece2 = pieceAt([cPos[0], 5], pieces)
        if next_piece1 == None:
          available_moves.append([cPos[0], 6])
          if next_piece2 == None:
            available_moves.append([cPos[0], 5])
      else:
        next_piece = pieceAt([cPos[0], cPos[1]-1], pieces)
        if next_piece == None:
          available_moves.append([cPos[0], cPos[1]-1])
    else:

      ## diagonal take black ##
      diagonal_piece1 = pieceAt([cPos[0]+1, cPos[1]+1], pieces)
      diagonal_piece2 = pieceAt([cPos[0]-1, cPos[1]+1], pieces)
      if not diagonal_piece1 == None:
        if diagonal_piece1.col == 'white':
          available_moves.append(diagonal_piece1.pos)
      if not diagonal_piece2 == None:
        if diagonal_piece2.col == 'white':
          available_moves.append(diagonal_piece2.pos)

      ## check block ##
      if cPos[1] == 2:
        next_piece1 = pieceAt([cPos[0], 3], pieces)
        next_piece2 = pieceAt([cPos[0], 4], pieces)
        if next_piece1 == None:
          available_moves.append([cPos[0], 3])
          if next_piece2 == None:
            available_moves.append([cPos[0], 4])
      else:
        next_piece = pieceAt([cPos[0], cPos[1]+1], pieces)
        if next_piece == None:
          available_moves.append([cPos[0], cPos[1]+1])

  ## rook ##
  elif move_piece.type == 'rook':
    moves = straight_rule(move_piece, pieces)

    for move in moves:
      available_moves.append(copy(move))
    del moves

  ## knight ##
  elif move_piece.type == 'knight':
    moves = [
      [cPos[0]-1, cPos[1]-2],
      [cPos[0]+1, cPos[1]-2],
      [cPos[0]+2, cPos[1]-1],
      [cPos[0]+2, cPos[1]+1],
      [cPos[0]+1, cPos[1]+2],
      [cPos[0]-1, cPos[1]+2],
      [cPos[0]-2, cPos[1]+1],
      [cPos[0]-2, cPos[1]-1]
    ]

    for move in moves:
      if 0 < move[0] < 9 and 0 < move[1] < 9:
        if (pieceAt(move, pieces) == None) or (pieceAt(move, pieces).col != move_piece.col):
          available_moves.append(move)

  ## bishop ##
  elif move_piece.type == 'bishop':
    moves = diagonal_rule(move_piece, pieces)

    for move in moves:
      available_moves.append(copy(move))
    del moves

  ## queen ##
  elif move_piece.type == 'queen':
    moves1 = straight_rule(move_piece, pieces)
    moves2 = diagonal_rule(move_piece, pieces)

    for move in moves1:
      available_moves.append(copy(move))
    del moves1

    for move in moves2:
      available_moves.append(copy(move))
    del moves2

  ## king ##
  else:
    if (len(move_piece.move_history) == 0):
      rooks = get_pieces(move_piece.col, 'rook', pieces)
      enemy_col = toggle_var(move_piece.col, 'white', 'black')
      for rook in rooks:
        if (len(rook.move_history) == 0):
          diff = rook.pos[0] - move_piece.pos[0]
          step = floor(diff/abs(diff))
          safe = False

          for i in range(0, step*3, step):
            step_pos = [move_piece.pos[0]+i, move_piece.pos[1]]
            step_piece = pieceAt(step_pos, pieces)
            if (step_piece == None) or (i == 0):
              if is_square_safe(step_pos, enemy_col, pieces, match_history):
                safe = True

          if safe:
            available_moves.append([move_piece.pos[0]+(step*2), move_piece.pos[1]])

    for i in range(-1, 2):
      for j in range(-1, 2):
        move = [cPos[0]+j, cPos[1]+i]
        target = pieceAt(move, pieces)

        if (not (i == 0 and j == 0)) or (target == None) or (target.col != move_piece.col):
          available_moves.append(move)

  return available_moves

def validate_move(game, snap_piece, new_x, new_y, skip_turn_check=False):
  if snap_piece.pos[0] == new_x and snap_piece.pos[1] == new_y:
    return [False, 'no move attempted']

  for piece in game.match.pieces:
    if (piece.pos[0] == new_x and piece.pos[1] == new_y and piece.col == snap_piece.col):
      return [False , 'no friendly fire!']

  if not (0 < new_x < 9 and 0 < new_y < 9):
    return [False, 'out of bouds']

  is_en_passant = False
  if (game.match.state == 'onGoing'):
    if (not game.match.turn == snap_piece.col) and (not skip_turn_check):
      return [False, 'let the other player play!']

    moves = get_moves_by_rule(snap_piece, game.match.pieces, game.match.move_history)
    valid_pos = False

    for move in moves:
      if new_x == move[0] and new_y == move[1]:
        if len(move) > 2:
          if move[2] == 'enPassant':
            is_en_passant = True

        valid_pos = True
        break

    if not valid_pos:
      return [False, 'invalid position']

    ## kings safety ##
    modded_pieces = []
    take_piece_modded = False

    for piece in game.match.pieces:
      modded_pieces.append(Piece(copy(piece.type), copy(piece.pos), copy(piece.col), game.match.board))
      if piece.pos[0] == snap_piece.pos[0] and piece.pos[1] == snap_piece.pos[1]:
        target = pieceAt([new_x, new_y], game.match.pieces)
        if target != None:
          take_piece_modded = True

    if take_piece_modded:
      modded_pieces.remove(pieceAt([new_x, new_y], modded_pieces))

    modded_snap_piece = pieceAt(snap_piece.pos, modded_pieces)
    modded_snap_piece.pos[0] = new_x
    modded_snap_piece.pos[1] = new_y

    if not is_square_safe(get_pieces(snap_piece.col, 'king', modded_pieces)[0].pos, toggle_var(snap_piece.col, 'white', 'black'), modded_pieces, game.match.move_history):
      return [False, 'kings safety', get_pieces(snap_piece.col, 'king', game.match.pieces)[0]]

  return [True, 'all good!', is_en_passant]
