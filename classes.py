import pygame
import datetime
from copy import copy
from math import ceil

class Piece:
  def __init__(self, type, pos, col, board):
    self.hover = False
    self.board = board
    self.type = type
    self.pos = pos
    self.col = col
    self.move_history = []
    min_board_dim = min(board.width, board.height)
    cell_size = ceil(min_board_dim/8)
    self.element = pygame.Rect(board.x + (cell_size * self.pos[0] - cell_size), board.y + (cell_size * self.pos[1] - cell_size), cell_size, cell_size)

    self.update_image(cell_size)

  def promote(self, type):
    if not self.type == 'pawn':
      return False

    self.type = type

    self.update_image(ceil(min(self.board.width, self.board.height)/8))
    #work in progress (maybe)

  def update_image(self, cell_size):
    img = pygame.image.load('assets/images/' + self.col + '_' + self.type + '.png')

    img_width = img.get_width()
    img_height = img.get_height()
    img_ratio = img_width/img_height

    if img_width > img_height:
      new_width = cell_size*.8
      new_height = img_ratio*new_width
    else:
      new_height = cell_size*.8
      new_width = img_ratio*new_height

    self.image = pygame.transform.scale(img, (new_width, new_height))
    self.align_image()

  def align_image(self):
    self.imgX = self.element.x + ((self.element.width-self.image.get_width())/2)
    self.imgY = self.element.y + ((self.element.height-self.image.get_height())/2)

class Match:
  def __init__(self, board, starting_pieces, default_positions):
    self.starting_pieces = starting_pieces
    self.default_positions = default_positions
    self.board = board
    self.pieces = []
    self.move_history = []
    self.promotion_history = []
    self.set_default_pieces()
    self.turn = None#/ white / black
    self.state = 'notStarted'#/ onGoing
    self.result = 'notConcluded'#/ white / black / draw

    self.reset_time()

    self.timers = {
      'white' : 600000,
      'black' : 600000
    }

    self.additional_time = {
      'white' : 0,
      'black' : 0
    }

  def reset_board(self):
    if self.state == 'onGoing':
      return False

    self.set_default_pieces()

  def start(self, total_time):
    if self.state == 'onGoing':
      return False

    self.timers = {
      'white' : 600000,
      'black' : 600000
    }

    self.additional_time = {
      'white' : 0,
      'black' : 0
    }

    self.set_default_pieces()
    self.turn = 'white'
    self.state = 'onGoing'

    self.reset_time()
    self.white_timestamp = total_time

  def reset_time(self):
    self.white_timestamp = None
    self.black_timestamp = None
    self.white_disc = 0
    self.black_disc = 0
    self.white_time = 0
    self.black_time = 0
    self.additional_time = {
      'white' : 0,
      'black' : 0
    }

  def end(self):
    self.state = 'notStarted'
    self.turn = None
    self.set_default_pieces()

  def switch_turns(self, total_time):
    if self.black_timestamp == None:
        self.black_timestamp = total_time

    if self.turn == 'white':
      self.black_disc = total_time - (self.black_timestamp + self.black_time)
    else:
      self.white_disc = total_time - (self.white_timestamp + self.white_time)

    if self.turn == 'white':
      self.turn = 'black'
    elif self.turn == 'black':
      self.turn = 'white'

  def conclude(self, result, nSaves, is_playback=False):
    ## save the match data and conclude the match ##
    if not (self.state == 'onGoing'):
      return None

    if not is_playback:
      match_data_str = ''

      for i in range(len(self.move_history)):
        move = self.move_history[i]
        match_data_str += f'{move[0][0]}{move[0][1]}{move[1][0]}{move[1][1]}'
        if not (self.promotion_history[i] == None):
          promo_type = self.promotion_history[i][1]
          print(promo_type)

          if promo_type == 'queen':
            match_data_str += 'q___'
          elif promo_type == 'rook':
            match_data_str += 'r___'
          elif promo_type == 'bishop':
            match_data_str += 'b___'
          else:
            match_data_str += 'k___'

      nSaves = int(open('data/nSaves', 'rt').read())

      open('data/nSaves', 'wt').write(f'{nSaves+1}')

      time = datetime.datetime.now()

      file_name = f'{time.year}-{time.month}-{time.day} {time.hour}-{time.minute}-{time.second}-{time.microsecond}'

      open(f'data/saves/{file_name}', 'w').write(match_data_str)
      open(f'data/savesList', 'a').write(f'{file_name}\n')

    self.state = 'notStarted'
    self.result = result
    print(result)

  def set_default_pieces(self):
    del self.pieces
    self.pieces = []
    self.move_history = []
    self.promotion_history = []

    for i in range(32):
      self.pieces.append(Piece(copy(self.starting_pieces[i].type), copy(self.default_positions[i]), copy(self.starting_pieces[i].col), self.board))

class Game:
  def __init__(self, screen, board):
    self.screen = screen
    b = board
    w = 'white'
    bl = 'black'

    self.default_positions = [
      #pawn                                                           #rook           #knight         #bishop         #queen  #king
      [1, 7], [2, 7], [3, 7], [4, 7], [5, 7], [6, 7], [7, 7], [8, 7], [1, 8], [8, 8], [2, 8], [7, 8], [3, 8], [6, 8], [4, 8], [5, 8], ## white ##
      [1, 2], [2, 2], [3, 2], [4, 2], [5, 2], [6, 2], [7, 2], [8, 2], [1, 1], [8, 1], [2, 1], [7, 1], [3, 1], [6, 1], [4, 1], [5, 1]  ## black ##
    ]

    self.default_pieces = [
      Piece('pawn', [1, 7], w, b),
      Piece('pawn', [2, 7], w, b),
      Piece('pawn', [3, 7], w, b),
      Piece('pawn', [4, 7], w, b),
      Piece('pawn', [5, 7], w, b),
      Piece('pawn', [6, 7], w, b),
      Piece('pawn', [7, 7], w, b),
      Piece('pawn', [8, 7], w, b),
      Piece('rook', [1, 8], w, b),
      Piece('rook', [8, 8], w, b),
      Piece('knight', [2, 8], w, b),
      Piece('knight', [7, 8], w, b),
      Piece('bishop', [3, 8], w, b),
      Piece('bishop', [6, 8], w, b),
      Piece('queen', [4, 8], w, b),
      Piece('king', [5, 8], w, b),

      Piece('pawn', [1, 2], bl, b),
      Piece('pawn', [2, 2], bl, b),
      Piece('pawn', [3, 2], bl, b),
      Piece('pawn', [4, 2], bl, b),
      Piece('pawn', [5, 2], bl, b),
      Piece('pawn', [6, 2], bl, b),
      Piece('pawn', [7, 2], bl, b),
      Piece('pawn', [8, 2], bl, b),
      Piece('rook', [1, 1], bl, b),
      Piece('rook', [8, 1], bl, b),
      Piece('knight', [2, 1], bl, b),
      Piece('knight', [7, 1], bl, b),
      Piece('bishop', [3, 1], bl, b),
      Piece('bishop', [6, 1], bl, b),
      Piece('queen', [4, 1], bl, b),
      Piece('king', [5, 1], bl, b)
    ]

    self.match = Match(board, self.default_pieces, self.default_positions)
