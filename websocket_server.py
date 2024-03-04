# -*- coding: utf-8 -*-
#!/usr/bin/python3
# Websocket server. Invoked by web page creating a websocket
# with url localhost:8081. websocketd.exe should be run via serve.bat.
# It will listen on port 8081, and launch this program when connected.
from websocketfuncs import *
from sys import stdin
import math, copy, random, time, threading


width = 10
height = 20
interval = 10
acceleration = 60
BLACK = 1
WHITE = 0


global score 
score = 0

class Tetromino():
  def __init__(self, shape):
        self.xpos = round(width/2)
        self.ypos = 0
        self.shape = shape
        if shape == "I":
           s = """\
X
X
X
X 
""" 
        elif shape == "J":
            s = """\
 X 
 X 
XX 
"""
            
        elif shape == "T":
          s = """\
XXX
 X 
"""
        elif shape == "S":
          s = """\
XX 
 XX
"""

        elif shape == "L":
           s = """\
X  
X  
XX 
"""     
        elif shape == "O":
            s = """\
XX
XX
"""
        elif shape == "Z":
          s = """\
 XX
XX 
"""
        self.bitmap = self.translate(s, shape)

  def translate(self, shape, form):
    bm = []
    b = shape
    if form is not 'I':
      b = shape.split('\n')
    for y in range(len(b)-1):
        for x in b[y]:
          if x == 'X': 
            bm.append(form)
          else:
            bm.append(0)
    if form in ('T','S','Z'):
        for _ in range(3):
          bm.append(0)
    return bm

  def advance(self):
        self.ypos += 1

  def shift_l(self):
        self.xpos -= 1

  def shift_r(self):
      self.xpos += 1

  def advance(self):
      self.ypos +=1


  def rotate(self):
    if len(self.bitmap) in (9,4):
        side = round(math.sqrt(len(self.bitmap)))
        new_tm = [0 for _ in range(len(self.bitmap)) ]
        for y in range(side):
          for x in range(side):
            i = y * side + x #index of Tm to be rotated
            j = ((x * side) + (round(side / 2)) - y) #index of cell after rotation translation
            new_tm[j] = self.bitmap[i]        
    elif (len(self.bitmap) == 8):        
      new_tm = [1,1,1,1,0]
    elif self.shape == 'I':
      new_tm  = [1,0,1,0,1,0,1,0]
    self.bitmap = copy.deepcopy(new_tm)

class Board:
  def __init__(self,height, width):
    self.board = []
    for y in range(height):
      for x in range(width+2):
        if x == 0 or x == width+1:
          self.board.append(BLACK)
        else:
          self.board.append(WHITE)
    for x in range(width+2):
      self.board.append(BLACK)

  def change(self, piece, action):
      prev_board = copy.copy(self.board)
      if len(piece.bitmap) in (9,4):
        sideH = round(math.sqrt(len(piece.bitmap)))
        sideW = round(math.sqrt(len(piece.bitmap)))
      elif (len(piece.bitmap) == 8):
        sideH = 4
        sideW = 2
      elif piece.shape == 'I':
        sideH = 1
        sideW = 4 
      for y in range(sideH):
        for x in range(sideW):
          i = y * sideW + x #index of Tetromino
          j = ((piece.ypos + y) * (width+2)) + piece.xpos + x  #index of board
          if (piece.bitmap[i] and not self.board[j] and action == 'add'):  #bitmap cell is 1 and board cell is zero
            prev_board[j] = piece.shape
          elif (piece.bitmap[i] and self.board[j] and action =='remove'):
            prev_board[j] = 0
          elif (piece.bitmap[i] and self.board[j] and action =='check-collision'):
            return True 
      self.board = copy.deepcopy(prev_board)
      
def row_finished(cur_board):
    rows = []
    row = 0
    for y in range(height):
        full = True
        for x in range(1,width+1):
          i = ((y* (width+2) + x))
          if not cur_board.board[i]:
              full = False
              break
        if full:
            rows.append(row)
        row +=1
    return rows




def slide_down(cur_board,rows):
    total_rows = 0
    blink_time = .25
    global score
    full_board = copy.deepcopy(cur_board)
    for row in rows:
        for x in range(1,width +1): 
          i = ((width+2)*row)+x
          cur_board.board[i] = 0
        total_rows +=1
    render(cur_board)
    for x in range(3):
        time.sleep(blink_time)
        render(full_board)
        time.sleep(blink_time)
        render(cur_board)

    score = score + (500 * 2**total_rows) 

    for k in range(total_rows):
        for row in range(rows[k],0,-1):
            for x in range(width+2):
              i = ((width+2)*(row-1))+x  #index of cell above target one
              j = ((width+2)*row)+x  #index of target cell
              if cur_board.board[i] != 1 and row <= height-1:
                    cur_board.board[j] = cur_board.board[i] 
    return True            

# decorator to define request functions & add NAME:func to dict
def addToDict(f=None, d={}): 
   if f : d[f.__name__.upper()] = f; return f
   return d  # return dict when called without f

@addToDict    
def m(req): # req: qs msg_index send message
  el, msgx = req.split()
  send(f'IM;#msg;{msg[el][msgx]}')

req_dict = addToDict() 

def get():
  d=stdin.readline()[:-1]
  return d

def receive(): # invoked by main thread
  myboard = Board(height, width)
  render(myboard)
  cur_peice = Tetromino('I')
  print(cur_peice.bitmap)
  myboard.change(cur_peice, "add") 
  render(myboard)

  while True: # get client request & pass to related function until disconnect
    last_move_was_advance = False 
    prev_piece = copy.copy(cur_peice)
    
    req = get()
    if not req: break # disconnected
    cons(req)
    if req == '37':
      myboard.change(cur_peice, "remove") 
      cur_peice.shift_l()
    if req == '38':
      myboard.change(cur_peice, "remove")
      cur_peice.rotate()
    if req == '39':
      myboard.change(cur_peice, "remove")
      cur_peice.shift_r()
    if req == '40':
      myboard.change(cur_peice, "remove")
      cur_peice.advance()
      last_move_was_advance = True
    if req == '32':
      myboard.change(cur_peice, "remove")
      render(myboard)
      while not myboard.change(cur_peice, "check-collision"):
        prev_piece = copy.copy(cur_peice)
        cur_peice.advance()
      print(cur_peice.ypos)
      last_move_was_advance = True
    if myboard.change(cur_peice, "check-collision"):
      cur_peice = copy.copy(prev_piece)
      if last_move_was_advance:
          shape = random.choice('IJTSLOZ')
          myboard.change(cur_peice, "add")
          next_piece = Tetromino(shape)
          cur_peice = next_piece
          last_move_was_advance = False
    if row_finished(myboard):
      rows = row_finished(myboard)
      slide_down(myboard, rows)
      render(myboard)      
    myboard.change(cur_peice, "add")
    render(myboard)
    send(req) 
    

    
def render(board):
  global score
  req = 'ID;canvas;' + str(board.board).strip('[]') +',Score '+str(score)
  send(req)
      


tx1 = time.time()

def timer():
  global interval
  global acceleration
  global tx1
  while True:
    tx2= time.time()
    if (tx2 - tx1) > interval:
      req = 'II;#msg;Down'     #advance piece
      send(req)
      print(True)
      if tx1-tx2 > acceleration:
        interval -= 1
        if interval <= 0.2:
            interval = 0.2
      tx1 = time.time()



threading.Thread(target=timer).start()
# ** MAIN **
receive() # run main thread in loop until get returns empty string


