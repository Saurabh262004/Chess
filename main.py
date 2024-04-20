import pygame as pg
from copy import copy
from draw import draw_text, draw_board, draw_pieces, draw_promo_pieces
from classes import Game, Piece
from math import ceil, floor
from processMoves import toggle_var, get_pieces, is_square_safe, get_moves_by_rule, validate_move, pieceAt

pg.init()
pg.mixer.init()

## setting up variables ##
icon = pg.image.load('assets/images/icon.png')

pg.display.set_icon(icon)

pg.display.set_caption('Chess game')

time = pg.time

clock = time.Clock()

total_time = time.get_ticks()

fps = 60

screen_width, screen_height = 960, 540

board_size = screen_height*.8

button_border_size = 2

game_state = None

game_state_indicator_x = None

game_conclusion = 'None'

elements = None

dummy_promo_screen = None

buttons = None

buttons_cosmetic = None

cell_size = None

fonts = None

current_audio = None

saves = {
  'on_screen' : False,
  'nSaves' : int(open('data/nSaves').read()),
  'list' : [],
  'start_index' : 0,
  'end_index' : None,
  'max_start_index' : None,
  'elements' : [],
  'start_playback' : False,
  'current_playback_frame' : 0,
  'current_playback_move' : 0,
  'moves_interval' : ,
  'promo_list' : [],
  'is_currently_on_promo' : None,
  'loaded_save_data' : None
}

b1ls1 = None
b1ls2 = None
b1le = None
b2ls1 = None
b2ls2 = None
b2le = None

def update_saves():
  global elements, saves

  saves['nSaves'] = int(open('data/nSaves').read())
  saves['list'] = []
  saves['elements'] = []

  raw_list = open('data/savesList').read()
  save_name = ''

  for char in raw_list:
    if char == '\n':
      saves['list'].append(save_name)
      save_name = ''
    else:
      save_name += char

  print(saves['nSaves'])

  for save in saves['list']:
    print(save)

  for i in range(saves['nSaves']):
    saves['elements'].append(pg.Rect(elements['load_match'].x, elements['load_match'].y+((elements['load_match'].height/5)*(i-saves['start_index'])), elements['load_match'].width, elements['load_match'].height/5))

  if saves['nSaves'] > 5:
    saves['max_start_index'] = saves['nSaves'] - 5
    saves['end_index'] = saves['start_index'] + 5
  else:
    saves['max_start_index'] = 0
    saves['end_index'] = saves['nSaves']

def move_list(direction):
  global saves, elements

  if direction == 'up' and saves['start_index'] > 0:
    for element in saves['elements']:
      element.y += (elements['load_match'].height/5)
    saves['start_index'] -= 1
    saves['end_index'] -= 1
  elif direction == 'down' and saves['start_index'] < saves['max_start_index']:
    for element in saves['elements']:
      element.y -= (elements['load_match'].height/5)
    saves['start_index'] += 1
    saves['end_index'] += 1

def load_save_data(file_name):
  global saves

  rd = open(f'data/saves/{file_name}').read() # raw data
  saves['loaded_save_data'] = []
  saves['promo_list'] = []

  for i in range(0, len(rd), 4):
    if rd[i].isdigit():
      saves['loaded_save_data'].append([[int(rd[i]), int(rd[i+1])], [int(rd[i+2]), int(rd[i+3])]])
    else:
      while ((len(saves['promo_list'])+1) < len(saves['loaded_save_data'])):
        saves['promo_list'].append(None)

      if rd[i] == 'q':
        saves['promo_list'].append('queen')
      elif rd[i] == 'r':
        saves['promo_list'].append('rook')
      elif rd[i] == 'b':
        saves['promo_list'].append('bishop')
      else:
        saves['promo_list'].append('knight')

  while (len(saves['promo_list']) < len(saves['loaded_save_data'])):
    saves['promo_list'].append(None)

  for i in range(len(saves['loaded_save_data'])):
    print(f'{saves['loaded_save_data'][i][0][0]}, {saves['loaded_save_data'][i][0][1]} -> {saves['loaded_save_data'][i][1][0]}, {saves['loaded_save_data'][i][1][1]} - {saves['promo_list'][i]}')

conclusion_anim = {
  'on' : False,
  'current_frame' : 0,
  'total_anim_frames' : round(250/(1000/fps)),
  'text_x' : 0
}

def play_audio(url, loops=0, start=0.0, fade_ms=0):
  global current_audio

  if not (url == current_audio):
    pg.mixer.music.unload()
    pg.mixer.music.load(url)

  pg.mixer.music.play(loops, start, fade_ms)
  current_audio = url

def resetElements():
  global saves, elements, board_size, dummy_promo_screen, screen_width, screen_height, buttons, buttons_cosmetic, game_state, game_state_indicator_x, cell_size, fonts, b1ls1, b1ls2, b1le, b2ls1, b2ls2, b2le

  board_size = screen_height*.8

  elements = {
    'board' : pg.Rect((screen_height - board_size)/2, (screen_height - board_size)/2, board_size, board_size),
    'control_panel' : pg.Rect(screen_width/1.5, 0, screen_width/3, screen_height),
    'timer_white' : pg.Rect(10, screen_height - 10 - (screen_height/23), (screen_height/23)*3, screen_height/23),
    'timer_black' : pg.Rect(10, 10, (screen_height/23)*3, screen_height/23),
    'promo_screen' : pg.Rect(screen_width/1.5, screen_height/6, screen_width/3, screen_height/8),
    'conclusion_screen' : pg.Rect(0, screen_height/7, screen_width, 0),
    'load_match' : pg.Rect(screen_width/4, screen_height/4, screen_width/2, screen_height/2),
    'list_up' : pg.Rect(((screen_width/4)*3)-30, (screen_height/4), 30, 30),
    'list_down' : pg.Rect(((screen_width/4)*3)-30, ((screen_height/4)*3)-30, 30, 30)
  }

  psx, psy, psw, psh = elements['promo_screen'].x, elements['promo_screen'].y, elements['promo_screen'].width, elements['promo_screen'].height

  dummy_promo_screen = pg.Rect(psx+(psw/10), psy+(psh/10), (psw-(psw/5))*2, (psh-(psh/5))*8)

  buttons = {
    'new_game' : pg.Rect((elements['control_panel'].x+(elements['control_panel'].width/2))-((elements['control_panel'].height*.22)/2), elements['control_panel'].height/2, elements['control_panel'].height*.216, elements['control_panel'].height*.04),
    'end_game' : pg.Rect((elements['control_panel'].x+(elements['control_panel'].width/2))-((elements['control_panel'].height*.192)/2), elements['control_panel'].height/1.7, elements['control_panel'].height*.192, elements['control_panel'].height*.04),
    'reset_board' : pg.Rect((elements['control_panel'].x+(elements['control_panel'].width/2))-((elements['control_panel'].height*.264)/2), elements['control_panel'].height/1.5, elements['control_panel'].height*.264, elements['control_panel'].height*.04),
    'load_match' : pg.Rect((elements['control_panel'].x+(elements['control_panel'].width/2))-((elements['control_panel'].height*.24)/2), elements['control_panel'].height/1.33, elements['control_panel'].height*.24, elements['control_panel'].height*.04)
  }

  buttons_cosmetic = {
    'new_game' : pg.Rect(buttons['new_game'].x - button_border_size, buttons['new_game'].y - button_border_size, buttons['new_game'].width + (button_border_size*2), buttons['new_game'].height + (button_border_size*2)),
    'end_game' : pg.Rect(buttons['end_game'].x - button_border_size, buttons['end_game'].y - button_border_size, buttons['end_game'].width + (button_border_size*2), buttons['end_game'].height + (button_border_size*2)),
    'reset_board' : pg.Rect(buttons['reset_board'].x - button_border_size, buttons['reset_board'].y - button_border_size, buttons['reset_board'].width + (button_border_size*2), buttons['reset_board'].height + (button_border_size*2)),
    'load_match' : pg.Rect(buttons['load_match'].x - button_border_size, buttons['load_match'].y - button_border_size, buttons['load_match'].width + (button_border_size*2), buttons['load_match'].height + (button_border_size*2))
  }

  cell_size = elements['board'].width/8

  fonts = {
    'buttons' : pg.font.SysFont('Courier New', floor(buttons['new_game'].height)),
    'timers' : pg.font.SysFont('Courier New', floor(elements['timer_white'].height)),
    'board_lables' : pg.font.SysFont('Courier New', floor(cell_size/4)),
    'conclusion' : pg.font.SysFont('Courier New', floor(screen_height/6)),
    'saves_list' : pg.font.SysFont('Courier New', floor(elements['load_match'].height/(5/0.5)))
  }

  saves['elements'] = []
  for i in range(saves['nSaves']):
    saves['elements'].append(pg.Rect(elements['load_match'].x, elements['load_match'].y+((elements['load_match'].height/5)*(i-saves['start_index'])), elements['load_match'].width, elements['load_match'].height/5))

  conclusion_text_x_reset()

  b1ls1 = [elements['list_up'].x+(elements['list_up'].width/4), (elements['list_up'].y+((elements['list_up'].height/4)*3))]
  b1ls2 = [elements['list_up'].x+((elements['list_up'].width/4)*3), (elements['list_up'].y+((elements['list_up'].height/4)*3))]
  b1le = [elements['list_up'].x+(elements['list_up'].width/2), (elements['list_up'].y+(elements['list_up'].height/4))]
  b2ls1 = [elements['list_down'].x+(elements['list_down'].width/4), elements['list_down'].y+(elements['list_down'].height/4)]
  b2ls2 = [elements['list_down'].x+((elements['list_down'].width/4)*3), elements['list_down'].y+(elements['list_down'].height/4)]
  b2le = [elements['list_down'].x+(elements['list_down'].width/2), (elements['list_down'].y+((elements['list_down'].height/4)*3))]


  if not game_state_indicator_x == None:
    game_state_indicator_x = (screen_width - (elements['control_panel'].width)/2)-((buttons['new_game'].height*.6)*(len(game_state)/2))

def conclusion_text_x_reset():
  global conclusion_anim

  conclusion_anim['text_x'] = (screen_width/2)-((len(game_conclusion)*((screen_height/6)*.6))/2)

resetElements()
update_saves()

screen = pg.display.set_mode((screen_width, screen_height), pg.RESIZABLE)

game = Game(screen, elements['board'])

def set_game_state():
  global game, game_state

  if game.match.state == 'onGoing':
    game_state = "In Match"
  else:
    game_state = "Free Mode"

set_game_state()

game_state_indicator_x = (screen_width - (elements['control_panel'].width)/2)-((buttons['new_game'].height*.6)*(len(game_state)/2))

promo_pieces = {
  'white' : [
    Piece('rook', [1, 1], 'white', dummy_promo_screen),
    Piece('knight', [2, 1], 'white', dummy_promo_screen),
    Piece('bishop', [3, 1], 'white', dummy_promo_screen),
    Piece('queen', [4, 1], 'white', dummy_promo_screen)
  ],
  'black' : [
    Piece('rook', [1, 1], 'black', dummy_promo_screen),
    Piece('knight', [2, 1], 'black', dummy_promo_screen),
    Piece('bishop', [3, 1], 'black', dummy_promo_screen),
    Piece('queen', [4, 1], 'black', dummy_promo_screen)
  ]
}

screen.fill('#885522')

promo_screen = False

mouse_down = False

valid_pickup = True

valid_snap = False

pickup_piece = None

snap_piece = None

second_resize = False

promo_piece = None

highlighted_tiles = []

availabe_moves_highlights = []

dangers_highlights = []

## recalibrates the UI dimensions ##
def reset_UI():
  global fonts, buttons, elements, dummy_promo_screen, promo_pieces, cell_size, screen_width, screen_height, game, second_resize

  ## all elements ##
  resetElements()

  ## pieces ##
  for piece in game.match.pieces:
    piece.board = elements['board']
    piece.element = pg.Rect(elements['board'].x + (cell_size * piece.pos[0] - cell_size), elements['board'].y + (cell_size * piece.pos[1] - cell_size), cell_size, cell_size)
    piece.update_image(cell_size)

  ## promo pieces ##
  dcs = min(dummy_promo_screen.width, dummy_promo_screen.height)/8 # dummy cell_size
  for i in range(2):
    col = 'white'
    if i == 1:
      col = 'black'

    for piece in promo_pieces[col]:
      piece.element = pg.Rect(dummy_promo_screen.x + (dcs * piece.pos[0] - dcs), dummy_promo_screen.y + (dcs * piece.pos[1] - dcs), dcs, dcs)
      piece.update_image(dcs)

  second_resize = not second_resize

## draws everything in the game ##
def draw_game():
  global screen, screen_width, screen_height, conclusion_anim, game_conclusion, game, elements, promo_screen, cell_size, buttons, game_state_indicator_x, fonts

  screen.fill('#51504c')

  ## board, pieces, control panel, promo_screen ##
  draw_board(screen, elements['board'], cell_size, highlighted_tiles, availabe_moves_highlights, dangers_highlights, fonts['board_lables'])
  draw_pieces(screen, game.match.pieces, pickup_piece)
  pg.draw.rect(screen, '#41403d', elements['control_panel'])
  pg.draw.rect(screen, '#2d2d2d', elements['promo_screen'])

  ## button and borders ##
  button1_col = '#51504c'
  button2_col = '#51504c'
  button3_col = '#51504c'
  button4_col = '#51504c'

  if buttons['new_game'].collidepoint(mouseX, mouseY):
    if mouse_down:
      button1_col = '#555555'
    else:
      button1_col = '#454545'
  elif buttons['end_game'].collidepoint(mouseX, mouseY):
    if mouse_down:
      button2_col = '#555555'
    else:
      button2_col = '#454545'
  elif buttons['reset_board'].collidepoint(mouseX, mouseY):
    if mouse_down:
      button3_col = '#555555'
    else:
      button3_col = '#454545'
  elif buttons['load_match'].collidepoint(mouseX, mouseY):
    if mouse_down:
      button4_col = '#555555'
    else:
      button4_col = '#454545'

  pg.draw.rect(screen, '#2d2c2a', buttons_cosmetic['new_game'])
  pg.draw.rect(screen, '#2d2c2a', buttons_cosmetic['end_game'])
  pg.draw.rect(screen, '#2d2c2a', buttons_cosmetic['reset_board'])
  pg.draw.rect(screen, '#2d2c2a', buttons_cosmetic['load_match'])

  pg.draw.rect(screen, button1_col, buttons['new_game'])
  pg.draw.rect(screen, button2_col, buttons['end_game'])
  pg.draw.rect(screen, button3_col, buttons['reset_board'])
  pg.draw.rect(screen, button4_col, buttons['load_match'])

  ## timers ##
  pg.draw.rect(screen, '#d2d2d2', elements['timer_white'])
  pg.draw.rect(screen, '#d2d2d2', elements['timer_black'])

  ## all the text ##
  draw_text(screen, game_state, fonts['buttons'], '#eeeeee', game_state_indicator_x, elements['promo_screen'].y/2)
  draw_text(screen, 'New Match', fonts['buttons'], '#eeeeee', buttons['new_game'].x, buttons['new_game'].y)
  draw_text(screen, 'End Game', fonts['buttons'], '#eeeeee', buttons['end_game'].x, buttons['end_game'].y)
  draw_text(screen, 'Reset Board', fonts['buttons'], '#eeeeee', buttons['reset_board'].x, buttons['reset_board'].y)
  draw_text(screen, 'Load Match', fonts['buttons'], '#eeeeee', buttons['load_match'].x, buttons['load_match'].y)

  wm = str(floor(game.match.timers['white']/60000))
  ws = str(floor(game.match.timers['white']/1000)%60)
  bm = str(floor(game.match.timers['black']/60000))
  bs = str(floor(game.match.timers['black']/1000)%60)

  if len(wm) < 2:
    wm = '0' + wm

  if len(ws) < 2:
    ws = '0' + ws

  if len(bm) < 2:
    bm = '0' + bm

  if len(bs) < 2:
    bs = '0' + bs

  time_white = wm + ':' + ws
  time_black = bm + ':' + bs

  draw_text(screen, time_white, fonts['timers'], '#111111', elements['timer_white'].x, elements['timer_white'].y)
  draw_text(screen, time_black, fonts['timers'], '#111111', elements['timer_black'].x, elements['timer_black'].y)

  if promo_screen:
    draw_promo_pieces(screen, promo_pieces[promo_piece.col])

  if conclusion_anim['on']:
    pg.draw.rect(screen, '#8eb963', elements['conclusion_screen'])
    if conclusion_anim['current_frame'] >= conclusion_anim['total_anim_frames']:
      draw_text(screen, game_conclusion, fonts['conclusion'], '#111111', conclusion_anim['text_x'], elements['conclusion_screen'].y+(elements['conclusion_screen'].height/4))

  if saves['on_screen']:
    pg.draw.rect(screen, '#2d2d2d', elements['load_match'])
    rcol1 = '#6ed664'
    rcol2 = '#d6ae64'

    for i in range(saves['start_index'], saves['end_index']):
      if (i % 2) == 0:
        rcol = rcol1
      else:
        rcol = rcol2

      pg.draw.rect(screen, rcol, saves['elements'][i])
      draw_text(screen, saves['list'][i], fonts['saves_list'], '#111111', elements['load_match'].x+5, saves['elements'][i].y+(saves['elements'][i].height/4))

    pg.draw.rect(screen, '#111111', elements['list_down'])
    pg.draw.rect(screen, '#111111', elements['list_up'])
    pg.draw.line(screen, '#eeeeee', b1ls1, b1le)
    pg.draw.line(screen, '#eeeeee', b1ls2, b1le)
    pg.draw.line(screen, '#eeeeee', b2ls1, b2le)
    pg.draw.line(screen, '#eeeeee', b2ls2, b2le)

## checks for a check mate or stale mate ##
def check_for_mate(col):
  global game

  valid_moves = 0
  enemy_col = col
  enemy_king = None

  for piece in game.match.pieces:
    if valid_moves > 1:
      break

    if piece.col == enemy_col:
      available_moves = get_moves_by_rule(piece, game.match.pieces, game.match.move_history)

      if piece.type == 'king':
        enemy_king = piece

      for move in available_moves:
        if validate_move(game, piece, move[0], move[1], True)[0]:
          valid_moves += 1

  if valid_moves < 1:
    if is_square_safe(enemy_king.pos, toggle_var(enemy_col, "white", "black"), game.match.pieces, game.match.move_history):
      return [True, "stale"]
    else:
      return [True, "check"]

  return [False]

## moves the piece that is to be snapped from the mouse position to a nearest square ##
def move_snap_piece(new_x=None, new_y=None):
  global game, elements, game_state, game_conclusion, promo_screen, snap_piece, promo_piece, total_time, dangers_highlights

  if new_x == None:
    new_x = ceil((snap_piece.element.x - elements['board'].x + (cell_size/2))/cell_size)
  if new_y == None:
    new_y = ceil((snap_piece.element.y - elements['board'].y + (cell_size/2))/cell_size)

  move_validation = validate_move(game, snap_piece, new_x, new_y)

  if move_validation[0]:
    dangers_highlights = []
    game.match.additional_time[snap_piece.col] += 5000
    enemy_col = toggle_var(snap_piece.col, 'white', 'black')
    castled = False

    ## castling ##
    if (snap_piece.type == 'king'):
      if ((abs(snap_piece.pos[0] - new_x) == 2) and (snap_piece.pos[1] == new_y) and (len(snap_piece.move_history) == 0)):
        distance = new_x - snap_piece.pos[0]
        if distance < 0:
          rook = pieceAt([1, snap_piece.pos[1]], game.match.pieces)
          rook.element.x = (elements['board'].width/2)
          rook.align_image()
          rook.pos[0] = 4
          castled = True
        else:
          rook = pieceAt([8, snap_piece.pos[1]], game.match.pieces)
          rook.element.x = (elements['board'].width/8)*6
          rook.align_image()
          rook.pos[0] = 6
          castled = True

    ## captures ##
    captured = False

    ## check if the move was an en passant and if so capture the pawn below the moved pawn ##
    if move_validation[2]:
      dir = -1
      if snap_piece.col == 'white':
        dir = 1

      game.match.pieces.remove(pieceAt([new_x, new_y+dir], game.match.pieces))
      captured = True

    elif castled:
      play_audio('assets/audio/castle.mp3')
    else:
      target = pieceAt([new_x, new_y], game.match.pieces)
      if target != None:
        game.match.pieces.remove(target)
        captured = True

    full_move = [copy(snap_piece.pos), [new_x, new_y], [copy(snap_piece.type), snap_piece.col]]

    game.match.move_history.append(full_move)
    snap_piece.move_history.append(full_move)

    snap_piece.pos[0] = new_x
    snap_piece.pos[1] = new_y

    enemy_king = get_pieces(enemy_col, 'king', game.match.pieces)
    check = False

    if len(enemy_king) > 0:
      check = (not is_square_safe(enemy_king[0].pos, snap_piece.col, game.match.pieces, game.match.move_history))

    ## promotion activation ##
    if (snap_piece.type == 'pawn') and (game.match.state == 'onGoing'):
      if snap_piece.col == 'white':
        if snap_piece.pos[1] == 1:
          promo_piece = snap_piece
          promo_screen = True
        else:
          promo_piece = None
          promo_screen = False
      else:
        if snap_piece.pos[1] == 8:
          promo_piece = snap_piece
          promo_screen = True
        else:
          promo_piece = None
          promo_screen = False

    if not promo_screen:
      game.match.promotion_history.append(None)

    mate = check_for_mate(enemy_col)

    if mate[0]:
      if mate[1] == "check":
        game.match.conclude(snap_piece.col, saves['nSaves'], saves['start_playback'])
        play_audio('assets/audio/check_mate.mp3')
        update_saves()
        if snap_piece.col == 'white':
          game_conclusion = 'White Wins!'
        else:
          game_conclusion = 'Black Wins!'
      else:
        game.match.conclude("Stale Mate", saves['nSaves'], saves['start_playback'])
        play_audio('assets/audio/stale_mate.mp3')
        update_saves()
        game_conclusion = 'Stale Mate!'

      conclusion_anim['on'] = True
      conclusion_text_x_reset()
    elif check:
      play_audio('assets/audio/check.mp3')
    elif captured:
      play_audio('assets/audio/capture.mp3')
    else:
      play_audio('assets/audio/move.mp3')

    if (game.match.state == 'onGoing') and (not promo_screen):
      game.match.switch_turns(total_time)

    set_game_state()

  elif move_validation[1] == 'kings safety':
    dangers_highlights.append(move_validation[2].pos)

  snap_piece.element.x = elements['board'].x + (cell_size * snap_piece.pos[0] - cell_size)
  snap_piece.element.y = elements['board'].y + (cell_size * snap_piece.pos[1] - cell_size)
  snap_piece.align_image()

  snap_piece = None
  print(f'fps: {clock.get_fps()}')

## main game loop ##
running = True
while running:
  mouseX, mouseY = pg.mouse.get_pos()
  eventButton = None

  ## time management ##
  total_time = time.get_ticks()

  if game.match.state == 'onGoing':
    if game.match.turn == 'white':
      game.match.white_time = (total_time - (game.match.white_timestamp + game.match.white_disc))
    else:
      game.match.black_time = (total_time - (game.match.black_timestamp + game.match.black_disc))

    game.match.timers['white'] = 600000 - game.match.white_time + 1000 + game.match.additional_time['white']
    if not game.match.black_timestamp == None:
      game.match.timers['black'] = 600000 - game.match.black_time + 1000 + game.match.additional_time['black']

    if game.match.timers['white'] <= 0:
      game.match.timers['white'] = 0
      game.match.conclude('black', saves['nSaves'], saves['start_playback'])
      update_saves()
      game_conclusion = 'Black Wins!'
      conclusion_anim['on'] = True
      conclusion_text_x_reset()
    elif game.match.timers['black'] <= 0:
      game.match.timers['black'] = 0
      game.match.conclude('white', saves['nSaves'], saves['start_playback'])
      update_saves()
      game_conclusion = 'White Wins!'
      conclusion_anim['on'] = True
      conclusion_text_x_reset()

  ## event handling ##
  for event in pg.event.get():
    if event.type == pg.QUIT:
      running = False

    elif event.type == pg.MOUSEBUTTONDOWN:
      mouse_down = True

      if event.button == 1:
        eventButton = 1
        if not saves['on_screen']:
          if buttons['new_game'].collidepoint(mouseX, mouseY) and not (game.match.state == 'onGoing'):
            game.match.start(total_time)
            reset_UI()
            print('New match started')
            play_audio('assets/audio/game_start.wav')
          elif buttons['end_game'].collidepoint(mouseX, mouseY) and (game.match.state == 'onGoing'):
            game.match.end()
            reset_UI()
            print('Game Aborted')
            play_audio('assets/audio/game_over.mp3')
            saves['start_playback'] = False
            saves['current_playback_move'] = 0
            saves['current_playback_frame'] = 0
            saves['is_currently_on_promo'] = False
          elif buttons['reset_board'].collidepoint(mouseX, mouseY) and not (game.match.state == 'onGoing'):
            game.match.set_default_pieces()
            reset_UI()
            print('Board reset')
          elif buttons['load_match'].collidepoint(mouseX, mouseY) and not (game.match.state == 'onGoing'):
            saves['on_screen'] = True

          if valid_pickup and (not saves['start_playback']):
            for piece in game.match.pieces:
              if piece.element.collidepoint(mouseX, mouseY):
                pickup_piece = piece
                valid_pickup = False
        else:
          if elements['list_up'].collidepoint(mouseX, mouseY):
            print('listUp')
            move_list('up')
          elif elements['list_down'].collidepoint(mouseX, mouseY):
            print('listDown')
            move_list('down')
          elif not elements['load_match'].collidepoint(mouseX, mouseY):
            saves['on_screen'] = False
          else:
            for i in range(saves['start_index'], saves['end_index']):
              if saves['elements'][i].collidepoint(mouseX, mouseY):
                load_save_data(saves['list'][i])
                saves['start_playback'] = True
                saves['on_screen'] = False
                print(len(saves['loaded_save_data']))
                print(saves['list'][i])
                game.match.start(total_time)
                reset_UI()
                break

        set_game_state()
      elif event.button == 3:
        eventButton = 3
        ## check user tile highlight ##
        if elements['board'].collidepoint(mouseX, mouseY):
          new_highlighted_tile = [floor((mouseX-elements['board'].x)/cell_size), floor((mouseY-elements['board'].y)/cell_size)]
          pop_tile = None

          for i in range(len(highlighted_tiles)):
            tile = highlighted_tiles[i]
            if tile[0] == new_highlighted_tile[0] and tile[1] == new_highlighted_tile[1]:
              pop_tile = i

          if pop_tile == None:
            highlighted_tiles.append(new_highlighted_tile)
          else:
            highlighted_tiles.pop(pop_tile)

    elif event.type == pg.MOUSEBUTTONUP:
      mouse_down = False
      snap_piece = pickup_piece

  if promo_screen and ((mouse_down and eventButton == 1) or (not saves['is_currently_on_promo'] == None)):
    col = promo_piece.col
    for piece in promo_pieces[col]:
      if piece.element.collidepoint(mouseX, mouseY) or (piece.type == saves['is_currently_on_promo']):
        promo_piece.promote(piece.type)
        game.match.promotion_history.append([promo_piece.pos, piece.type])

        if (game.match.state == 'onGoing'):
          game.match.switch_turns(total_time)
          mate = check_for_mate(toggle_var(promo_piece.col, 'white', 'black'))

          if mate[0]:
            if mate[1] == "check":
              game.match.conclude(promo_piece.col, saves['nSaves'], saves['start_playback'])
              update_saves()
              if promo_piece.col == 'white':
                game_conclusion = 'White Wins!'
              else:
                game_conclusion = 'Black Wins!'
            else:
              game.match.conclude("Stale Mate", saves['nSaves'], saves['start_playback'])
              update_saves()
              game_conclusion = 'Stale Mate!'

            conclusion_anim['on'] = True
            conclusion_text_x_reset()

          promo_piece = None
          promo_screen = False

  if conclusion_anim['on']:
    if conclusion_anim['current_frame'] >= (fps*1.5):
      conclusion_anim['on'] = False
      conclusion_anim['current_frame'] = 0
      elements['conclusion_screen'].height = 0
    else:
      conclusion_anim['current_frame'] += 1

      if conclusion_anim['current_frame'] <= conclusion_anim['total_anim_frames']:
        elements['conclusion_screen'].height = ((screen_height/3)/conclusion_anim['total_anim_frames'])*conclusion_anim['current_frame']

  if not mouse_down:
    valid_pickup = True
    pickup_piece = None

  if (not snap_piece == None) and (not saves['start_playback']):
    move_snap_piece()

  if saves['start_playback']:
    saves['current_playback_frame'] += 1
    if saves['current_playback_move'] >= len(saves['loaded_save_data']):
      saves['start_playback'] = False
      saves['current_playback_frame'] = 0
      saves['current_playback_move'] = 0
    elif (saves['current_playback_frame']%saves['moves_interval'] == 0):
      saves['is_currently_on_promo'] = saves['promo_list'][saves['current_playback_move']]
      move = saves['loaded_save_data'][saves['current_playback_move']]
      snap_piece = pieceAt(move[0], game.match.pieces)
      move_snap_piece(move[1][0], move[1][1])
      saves['current_playback_move'] += 1

  tmp_sh = screen.get_height()
  tmp_sw = screen.get_width()
  screen_change = False

  if not (screen_height == tmp_sh) or not (screen_width == tmp_sw):
    screen_height = tmp_sh
    screen_width = tmp_sw
    screen_change = True

  if second_resize or screen_change:
    reset_UI()

  if not valid_pickup:
    pickup_piece.element.x = mouseX - (elements['board'].width/16)
    pickup_piece.element.y = mouseY - (elements['board'].height/16)
    pickup_piece.align_image()

  if (not pickup_piece == None):
    if (len(availabe_moves_highlights) == 0):
      availabe_moves_highlights = get_moves_by_rule(pickup_piece, game.match.pieces, game.match.move_history)
  else:
    availabe_moves_highlights = []

  draw_game()

  pg.display.flip()
  clock.tick(fps)

pg.quit()
