import pygame

norm_white = pygame.Color(233, 237, 204)
norm_green = pygame.Color(119, 153, 84)
userHigh_white = pygame.Color(244, 246, 128)
userHigh_green = pygame.Color(187, 204, 68)
move_high = pygame.Color(100, 100, 100)
dangerHigh_green = pygame.Color(245, 105, 105)
dangerHigh_white = pygame.Color(243, 141, 125)
board_text_col = pygame.Color(2, 2, 2)

boardInd = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

def same_col(col1, col2):
  if col1.r == col2.r and col1.g == col2.g and col1.b == col2.b and col1.a == col2.a:
    return True
  return False

def toggle_col(col, col1, col2):
  if same_col(col, col1):
    return col2
  elif same_col(col, col2):
    return col1
  return col

def draw_text(screen, text, font, text_col, x, y):
  img = font.render(text, True, text_col)
  screen.blit(img, (x, y))

def draw_board(screen, board, cell_size, user_highlights, availabe_moves_highlights, danger_highlights, board_font):
  col = norm_green

  for i in range(8):
    col = toggle_col(col, norm_green, norm_white)
    highlight_col = None

    for j in range(8):
      user_highlight = False
      move_highlight = False
      danger_highlight = False
      cellX, cellY = (j*cell_size)+board.x, (i*cell_size)+board.y

      ## check for any highlights ##
      for tile in user_highlights:
        if tile[0] == j and tile[1] == i:
          user_highlight = True

      for tile in availabe_moves_highlights:
        if tile[0] == j+1 and tile[1] == i+1:
          move_highlight = True

      for tile in danger_highlights:
        if tile[0] == j+1 and tile[1] == i+1:
          danger_highlight = True

      ## draw highlights if available if not draw the usual square ##
      if not user_highlight and not danger_highlight:
        pygame.draw.rect(screen, col, (cellX, cellY, cell_size, cell_size))
      else:
        if user_highlight:
          if same_col(col, norm_white):
            highlight_col = userHigh_white
          else:
            highlight_col = userHigh_green
        else:
          if same_col(col, norm_white):
            highlight_col = dangerHigh_white
          else:
            highlight_col = dangerHigh_green
        pygame.draw.rect(screen, highlight_col, (cellX, cellY, cell_size, cell_size))

      if move_highlight:
        highlight_col = move_high
        pygame.draw.circle(screen, highlight_col, ((j*cell_size)+(cell_size/2)+board.x, (i*cell_size)+(cell_size/2)+board.y), cell_size/6)

      if j == 0:
        draw_text(screen, f'{i+1}', board_font, board_text_col, cellX, cellY)

      if i == 7:
        draw_text(screen, boardInd[j], board_font, board_text_col, cellX+((cell_size/4)*3), cellY+((cell_size/4)*3))

      col = toggle_col(col, norm_green, norm_white)

def draw_promo_pieces(screen, pieces):
  for piece in pieces:
    screen.blit(piece.image, (piece.imgX, piece.imgY))

def draw_pieces(screen, pieces, pickup_piece):
  #work in progress

  for piece in pieces:
    if ((pickup_piece == None) or (not (pickup_piece.pos[0] == piece.pos[0] and pickup_piece.pos[1] == piece.pos[1] and pickup_piece.col == piece.col))):
      screen.blit(piece.image, (piece.imgX, piece.imgY))

  if (not pickup_piece == None):
    screen.blit(pickup_piece.image, (pickup_piece.imgX, pickup_piece.imgY))
