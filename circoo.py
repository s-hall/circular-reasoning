import pygame as pg
import pygame.gfxdraw as draw
import math
from math import pi
import copy
import sys
import time
from font import cFontManager

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  0, 255,   0)
RED =   (255,   0,   0)
YELLOW = (255, 255, 0)
BROWN = (191, 112,   6)
PINK = (255, 0, 144)

def mod_add(x, y, mod):
    if y >= 0: return (x+y)%mod
    z = x+y
    if z < 0: return z + mod
    return z

def circle(screen, x, y, color, layer, r=20):
    pg.draw.circle(screen, color, (int(x),int(y)), r)
    if layer == "end": pg.draw.circle(screen, BLACK, (int(x),int(y)), 8)

def trigon(screen, x, y, color, layer, r=20):
    x1 = x; y1 = y - r
    x2 = x + r * math.cos(pi/6)
    y2 = y + r * math.sin(pi/6)
    x3 = x - r * math.cos(pi/6)
    y3 = y2
    draw.filled_trigon(screen, int(x1), int(y1), int(x2), int(y2), int(x3), int(y3), color)
    if layer == "end": pg.draw.circle(screen, BLACK, (int(x),int(y)), 8)

def square(screen, x, y, color, layer, r=20):
    pg.draw.rect(screen, color, (x-r, y-r, 2*r, 2*r))
    if layer == "end": pg.draw.circle(screen, BLACK, (int(x),int(y)), 8)

class Piece:
    def __init__(self, shape, draw_fcn):
        self.shape = shape
        self.slice = 0
        self.layer = "start"
        self.draw_fcn = draw_fcn

class Player:
    def __init__(self, color):
        self.color = color
        self.circle = Piece(2, circle)
        self.triangle = Piece(3, trigon)
        self.square = Piece(4, square)

    def get_piece(self, shape):
        if shape == 2: return self.circle
        if shape == 3: return self.triangle
        if shape == 4: return self.square

    def check_win(self):
        return self.circle.layer == self.triangle.layer == self.square.layer == "end"

class Game:
    def __init__(self, players, kb, slices=16, width=750, height=750):
        self.keyboard_mode = kb
        pg.init()
        pg.font.init()
        self.screen = pg.display.set_mode((height,width))
        self.clock = pg.time.Clock()
        self.font = cFontManager(((None,12),(None,24)))
        self.fps = 10
        self.pause = 0

        self.width = width
        self.height = height
        self.cx = width//2
        self.cy = height//2

        self.slices = slices
        self.slice_ang = math.radians(360/slices)
        self.out = pg.Rect(25,25,700,700)
        self.out_r = 350
        self.mid = pg.Rect(125,125,500,500)
        self.mid_r = 250
        self.inn = pg.Rect(225,225,300,300)
        self.inn_r = 150
        self.cen = pg.Rect(325,325,100,100)
        self.cen_r = 50
        self.thresh = pi/64

        self.mid_gate = self.inn_gate = self.cen_gate = slices//2
        self.num_players = players
        self.players = []
        for p in range(players):
            if p == 0: col = RED
            if p == 1: col = BLUE
            if p == 2: col = GREEN
            if p == 3: col = YELLOW
            self.players.append(Player(col))
        self.current_player = 0
        self.current_moves = []
        self.last_move = ()
        self.first_player = 0
        self.last_player = players-1
        self.win = -1
        self.clicked = 0
        self.sel = -1

    def get_num_players(self, layer):
        num = 0
        for p in self.players:
            for piece in [p.circle, p.triangle, p.square]:
                if piece.layer == layer:
                    num += 1
        return num

    def get_arc_point(self, slice, r):
        ang = slice * self.slice_ang
        x = self.cx + r * math.cos(ang)
        y = self.cy - r * math.sin(ang)
        return (x, y)

    def slice_center(self, slice, layer):
        next = mod_add(slice, 1, self.slices)
        if layer == "out":
            layer_r = self.out_r
            next_r = self.mid_r
        if layer == "mid":
            layer_r = self.mid_r
            next_r = self.inn_r
        if layer == "inn":
            layer_r = self.inn_r
            next_r = self.cen_r
        (x1,y1) = self.get_arc_point(slice, layer_r)
        (x2,y2) = self.get_arc_point(next, layer_r)
        (x3,y3) = self.get_arc_point(slice, next_r)
        (x4,y4) = self.get_arc_point(next, next_r)
        return ((x1+x2+x3+x4)/4 , (y1+y2+y3+y4)/4)

    def occupied(self, slice, layer):
        for p in self.players:
            for piece in [p.circle, p.triangle, p.square]:
                if piece.slice == slice and piece.layer == layer:
                    return True
        return False

    # direc is either, forward, back
    def check_layer(self, slice, layer, shape, direc):
        moves = []
        if shape == -1:
            return []
        for sign in [1, -1]:
            if self.mid_gate == slice:
                # inward through mid
                if layer == "out" and not self.occupied(slice, "mid"):
                    if not direc == "back":
                        moves += self.check_layer(slice, "mid", shape-1, "forward")
                # outward through mid
                if layer == "mid" and not self.occupied(slice, "out"):
                    if not direc == "forward":
                        moves += self.check_layer(slice, "out", shape-1, "back")
            if self.inn_gate == slice:
                # inward through inn
                if layer == "mid" and not self.occupied(slice, "inn"):
                    if not direc == "back":
                        moves += self.check_layer(slice, "inn", shape-1, "forward")
                # outward through inn
                if layer == "inn" and not self.occupied(slice, "mid"):
                    if not direc == "forward":
                        moves += self.check_layer(slice, "mid", shape-1, "back")
            if self.cen_gate == slice:
                if layer == "inn" and shape == 1:
                        moves += [(-1, "end")]

            new_slice = slice
            speed = shape
            while(speed > 0):
                new_slice = mod_add(new_slice, sign, self.slices)
                while(self.occupied(new_slice, layer)):
                    new_slice = mod_add(new_slice, sign, self.slices)
                speed -= 1

                if self.mid_gate == new_slice:
                    # inward through mid
                    if layer == "out" and not self.occupied(new_slice, "mid"):
                        if not direc == "back":
                            moves += self.check_layer(new_slice, "mid", speed-1, "forward")
                    # outward through mid
                    if layer == "mid" and not self.occupied(new_slice, "out"):
                        if not direc == "forward":
                            moves += self.check_layer(new_slice, "out", speed-1, "back")
                if self.inn_gate == new_slice:
                    # inward through inn
                    if layer == "mid" and not self.occupied(new_slice, "inn"):
                        if not direc == "back":
                            moves += self.check_layer(new_slice, "inn", speed-1, "forward")
                    # outward through inn
                    if layer == "inn" and not self.occupied(new_slice, "mid"):
                        if not direc == "forward":
                            moves += self.check_layer(new_slice, "mid", speed-1, "back")
                if self.cen_gate == new_slice:
                    if layer == "inn" and speed == 1:
                            moves += [(-1, "end")]

            moves.append((new_slice, layer))
        return moves

    def get_moves(self, piece):
        if piece.layer == "end":
            return []
        shape = piece.shape
        layer = piece.layer
        if layer == "start":
            if self.occupied(0, "out"):
                return []
            layer = "out"
            shape -= 1
        self.current_moves = list(set(self.check_layer(piece.slice, layer, shape, "either")))

    def do_move(self, move, piece):
        (slice, layer) = self.current_moves[move]
        self.last = copy.deepcopy(self.players)
        piece.slice = slice
        piece.layer = layer
        if self.players[self.current_player].check_win():
            self.win = self.current_player
        if self.current_player == self.last_player:
            self.last_player = self.first_player
            self.first_player = mod_add(self.first_player, 1, self.num_players)
            self.current_player = -1
        else:
            self.current_player = mod_add(self.current_player, 1, self.num_players)
        self.current_moves = []
        self.sel = -1

    def draw_board(self):
        # layer circles
        c = (self.cx, self.cy)
        pg.draw.circle(self.screen, BLACK, c, 350, 10)
        pg.draw.circle(self.screen, BLACK, c, 250, 10)
        pg.draw.circle(self.screen, BLACK, c, 150, 10)
        pg.draw.circle(self.screen, BLACK, c, 50, 0)
        pg.draw.arc(self.screen, PINK, self.out, 0, self.slice_ang+self.thresh, 10)
        # dividing lines
        for slice in range(self.slices):
            start = self.get_arc_point(slice, self.out_r)
            pg.draw.line(self.screen, BLACK, start, c)
        # current player in middle
        if self.current_player == -1:
            pg.draw.circle(self.screen, WHITE, c, 40, 0)
        else:
            pg.draw.circle(self.screen, self.players[self.current_player].color, c, 40, 0)
        # gates
        if self.current_player == -1: # rotate them
            if self.pause == self.fps:
                self.mid_gate = mod_add(self.mid_gate, -self.get_num_players("out"), self.slices)
            if self.pause == 2*self.fps:
                self.inn_gate = mod_add(self.inn_gate, -self.get_num_players("mid"), self.slices)
            if self.pause == 3*self.fps:
                self.cen_gate = mod_add(self.cen_gate, -self.get_num_players("inn"), self.slices)
                self.current_player = self.first_player
                self.pause = -1
            self.pause += 1
        pg.draw.arc(self.screen, WHITE, self.mid, self.mid_gate*self.slice_ang, (self.mid_gate+1)*self.slice_ang+self.thresh, 10)
        pg.draw.arc(self.screen, WHITE, self.inn, self.inn_gate*self.slice_ang, (self.inn_gate+1)*self.slice_ang+self.thresh, 10)
        pg.draw.arc(self.screen, WHITE, self.cen, self.cen_gate*self.slice_ang, (self.cen_gate+1)*self.slice_ang+self.thresh, 10)
        # players
        off = 50
        for p in self.players:
            for piece in [p.circle, p.triangle, p.square]:
                if piece.layer == "start" or piece.layer == "end":
                    if p.color == RED:
                        if piece.shape == 2:
                            x = off; y = off
                        if piece.shape == 3:
                            x = 2*off; y = off
                        if piece.shape == 4:
                            x = off; y = 2*off
                    if p.color == BLUE:
                        if piece.shape == 2:
                            x = self.width-off; y = off
                        if piece.shape == 3:
                            x = self.width-(2*off); y = off
                        if piece.shape == 4:
                            x = self.width-off; y = 2*off
                    if p.color == GREEN:
                        if piece.shape == 2:
                            x = off; y = self.height-off
                        if piece.shape == 3:
                            x = 2*off; y = self.height-off
                        if piece.shape == 4:
                            x = off; y = self.height-(2*off)
                    if p.color == YELLOW:
                        if piece.shape == 2:
                            x = self.width-off; y = self.height-off
                        if piece.shape == 3:
                            x = self.width-(2*off); y = self.height-off
                        if piece.shape == 4:
                            x = self.width-off; y = self.height-(2*off)
                    piece.draw_fcn(self.screen, x, y, p.color, piece.layer)
                else:
                    (x,y) = self.slice_center(piece.slice, piece.layer)
                    piece.draw_fcn(self.screen, x, y, p.color, piece.layer)
                if game.sel == piece.shape and piece.layer != "end" and p.color == self.players[self.current_player].color:
                    circle(self.screen, x, y, WHITE, "", 8)
        # possible moves
        if self.keyboard_mode:
            letter = ord("A")
            for (slice, layer) in self.current_moves:
                if slice == -1: # center
                    circle(self.screen, self.cx, self.cy, BLACK, "", 15)
                    game.font.Draw(self.screen,None,24,chr(letter),(self.cx-6,self.cy-8),WHITE,'center','center',True)
                else:
                    (x,y) = self.slice_center(slice, layer)
                    circle(self.screen, x, y, BLACK, "", 15)
                    game.font.Draw(self.screen,None,24,chr(letter),(x-6,y-8),WHITE,'center','center',True)
                letter += 1
        # order
        if self.num_players == 2: b = 35
        if self.num_players == 3: b = 55
        if self.num_players == 4: b = 75
        p = self.first_player
        for i in range(self.num_players):
            pg.draw.rect(self.screen, self.players[p].color, (self.cx-b+(mod_add(p,-self.first_player,self.num_players)*40),5,30,10))
            p = mod_add(p, 1, self.num_players)

    def closest_slice(self, x, y):
        for layer in ["out", "mid", "inn"]:
            for slice in range(self.slices):
                (cx, cy) = self.slice_center(slice, layer)
                if layer == "out": err = 35
                if layer == "mid": err = 25
                if layer == "inn": err = 15
                collision = pg.Rect(cx-err,cy-err,err*2,err*2)
                if collision.collidepoint(x, y):
                    return (slice, layer)
        collision = pg.Rect(self.cx-err,self.cy-err,err*2,err*2)
        if collision.collidepoint(x, y):
            return (-1, "end")
        return 0

game = Game(int(sys.argv[1]), int(sys.argv[2]))
while(1):
    for event in pg.event.get():
        if event.type == pg.QUIT: exit()
        if event.type == pg.MOUSEBUTTONDOWN and game.sel != -1 and not game.keyboard_mode:
            (x, y) = event.pos
            game.clicked = game.closest_slice(x, y)
            if game.clicked in game.current_moves:
                game.do_move(game.current_moves.index(game.clicked), curr.get_piece(game.sel))
        if event.type == pg.KEYDOWN:
            if game.current_player != -1:
                curr = game.players[game.current_player]
                if event.key == ord('1'):
                    game.current_moves = []
                    game.sel = -1
                if event.key == ord('2'):
                    game.sel = 2
                    game.get_moves(curr.get_piece(game.sel))
                if event.key == ord('3'):
                    game.sel = 3
                    game.get_moves(curr.get_piece(game.sel))
                if event.key == ord('4'):
                    game.sel = 4
                    game.get_moves(curr.get_piece(game.sel))
                if event.key == ord('u') and game.current_player != game.first_player:
                    game.current_player = mod_add(game.current_player, -1, game.num_players)
                    game.players = copy.deepcopy(game.last)
                    if game.sel != -1:
                        game.get_moves(game.players[game.current_player].get_piece(game.sel))
                if game.current_moves != [] and game.sel != -1 and game.keyboard_mode:
                    l = len(game.current_moves)
                    if event.key - ord('a') >= 0 and event.key - ord('a') < l:
                        game.do_move(event.key - ord('a'), curr.get_piece(game.sel))
                        game.sel = -1
    game.clock.tick(game.fps)
    game.screen.fill(BROWN)
    if game.win == -1:
        game.draw_board()
    else:
        if game.win == 0: print("Red wins!")
        if game.win == 1: print("Blue wins!")
        if game.win == 2: print("Green wins!")
        if game.win == 3: print("Yellow wins!")
        exit()
    pg.display.flip()
