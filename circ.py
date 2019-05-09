import pygame as pg
import pygame.gfxdraw as draw
import math
from math import pi
import copy
import sys
from font import cFontManager

pg.init()
pg.font.init()

font = cFontManager(((None,12),(None,24)))

width, height = 750, 750
c = cx, cy = width//2, height//2
screen = pg.display.set_mode((height,width))

clock = pg.time.Clock()

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  0, 255,   0)
RED =   (255,   0,   0)
YELLOW = (255, 255, 0)
BROWN = (191, 112,   6)
PINK = (255, 0, 144)

slices = 16
slice_ang = math.radians(360/slices)

out = pg.Rect(25,25,700,700); out_r = 350
mid = pg.Rect(125,125,500,500); mid_r = 250
inn = pg.Rect(225,225,300,300); inn_r = 150
cen = pg.Rect(325,325,100,100); cen_r = 50
thresh = pi/64

# game globals
mid_gate = inn_gate = cen_gate = slices//2
data = old_data = []
players = int(sys.argv[1])
for p in range(players):
    if p == 0: col = RED
    if p == 1: col = BLUE
    if p == 2: col = GREEN
    if p == 3: col = YELLOW
    # circle, triangle, square
    data.append([col, ["dead", 0], ["dead", 0], ["dead", 0]])

current = 0
first_player = 0
last_player = players-1
possible_moves = []
win = -1

def mod_add(x, y, m):
    if y >= 0: return (x+y)%m
    z = x+y
    if z < 0: return z + m
    return z

def get_num_players(layer):
    num = 0
    for p in data:
        for piece in range(1,4):
            if p[piece][0] == layer: num += 1
    return num

def get_arc_point(n, layer_r):
    ang = n*slice_ang
    x = cx + layer_r * math.cos(ang)
    y = cy - layer_r * math.sin(ang)
    return (x,y)

def slice_center(n, layer):
    next = mod_add(n,1,slices)
    if layer == "out":
        layer_r = out_r
        next_r = mid_r
    if layer == "mid":
        layer_r = mid_r
        next_r = inn_r
    if layer == "inn":
        layer_r = inn_r
        next_r = cen_r
    (x1,y1) = get_arc_point(n, layer_r)
    (x2,y2) = get_arc_point(next, layer_r)
    (x3,y3) = get_arc_point(n, next_r)
    (x4,y4) = get_arc_point(next, next_r)
    return ((x1+x2+x3+x4)/4 , (y1+y2+y3+y4)/4)

def trigon(x, y, color, extra):
    r = 20
    x1 = x; y1 = y - r
    x2 = x + r * math.cos(pi/6)
    y2 = y + r * math.sin(pi/6)
    x3 = x - r * math.cos(pi/6)
    y3 = y2
    draw.filled_trigon(screen, int(x1), int(y1), int(x2), int(y2), int(x3), int(y3), color)
    if extra: pg.draw.circle(screen, BLACK, (int(x),int(y)), 8)

def square(x, y, color, extra):
    r = 20
    pg.draw.rect(screen, color, (x-r, y-r, 2*r, 2*r))
    if extra: pg.draw.circle(screen, BLACK, (int(x),int(y)), 8)

def circle(x, y, color, extra, r=20):
    pg.draw.circle(screen, color, (int(x),int(y)), r)
    if extra: pg.draw.circle(screen, BLACK, (int(x),int(y)), 8)

def draw_board():
    global current
    global mid_gate
    global inn_gate
    global cen_gate

    # initial circles
    pg.draw.circle(screen, BLACK, c, 350, 10)
    pg.draw.circle(screen, BLACK, c, 250, 10)
    pg.draw.circle(screen, BLACK, c, 150, 10)
    pg.draw.circle(screen, BLACK, c, 50, 0)
    pg.draw.arc(screen, PINK, out, 0, slice_ang+thresh, 10)
    # dividing lines
    for i in range(slices):
        start = get_arc_point(i, out_r)
        pg.draw.line(screen, BLACK, start, c)
    # current player in middle
    if current < 0: pg.draw.circle(screen, WHITE, c, 40, 0)
    else: pg.draw.circle(screen, data[current][0], c, 40, 0)
    # gates
    if current >= 0:
        pg.draw.arc(screen, WHITE, mid, mid_gate*slice_ang, (mid_gate+1)*slice_ang+thresh, 10)
        pg.draw.arc(screen, WHITE, inn, inn_gate*slice_ang, (inn_gate+1)*slice_ang+thresh, 10)
        pg.draw.arc(screen, WHITE, cen, cen_gate*slice_ang, (cen_gate+1)*slice_ang+thresh, 10)
    else:
        if current == -1:
            mid_gate = mod_add(mid_gate, -get_num_players("out"), slices)
            current -= 1
            pg.draw.arc(screen, WHITE, mid, mid_gate*slice_ang, (mid_gate+1)*slice_ang+thresh, 10)
            pg.draw.arc(screen, WHITE, inn, inn_gate*slice_ang, (inn_gate+1)*slice_ang+thresh, 10)
            pg.draw.arc(screen, WHITE, cen, cen_gate*slice_ang, (cen_gate+1)*slice_ang+thresh, 10)
            pg.time.wait(1000)
        elif current == -2:
            inn_gate = mod_add(inn_gate, -get_num_players("mid"), slices)
            current -= 1
            pg.draw.arc(screen, WHITE, mid, mid_gate*slice_ang, (mid_gate+1)*slice_ang+thresh, 10)
            pg.draw.arc(screen, WHITE, inn, inn_gate*slice_ang, (inn_gate+1)*slice_ang+thresh, 10)
            pg.draw.arc(screen, WHITE, cen, cen_gate*slice_ang, (cen_gate+1)*slice_ang+thresh, 10)
            pg.time.wait(1000)
        elif current == -3:
            cen_gate = mod_add(cen_gate, -get_num_players("inn"), slices)
            current = first_player
            pg.draw.arc(screen, WHITE, mid, mid_gate*slice_ang, (mid_gate+1)*slice_ang+thresh, 10)
            pg.draw.arc(screen, WHITE, inn, inn_gate*slice_ang, (inn_gate+1)*slice_ang+thresh, 10)
            pg.draw.arc(screen, WHITE, cen, cen_gate*slice_ang, (cen_gate+1)*slice_ang+thresh, 10)
            pg.time.wait(1000)

    # players
    off = 50
    for p in data:
        for piece in range(3):
            layer = p[piece+1][0]
            slice = p[piece+1][1]
            shape = piece+2
            col = p[0]
            if layer == "dead" or layer == "done":
                if layer == "done": extra = True
                else: extra = False
                if col == RED:
                    if shape == 2: circle(off,off,col,extra)
                    if shape == 3: trigon(2*off,off,col,extra)
                    if shape == 4: square(off,2*off,col,extra)
                if col == BLUE:
                    if shape == 2: circle(width-off,off,col,extra)
                    if shape == 3: trigon(width-(2*off),off,col,extra)
                    if shape == 4: square(width-off,2*off,col,extra)
                if col == GREEN:
                    if shape == 2: circle(off,height-off,col,extra)
                    if shape == 3: trigon(2*off,height-off,col,extra)
                    if shape == 4: square(off,height-(2*off),col,extra)
                if col == YELLOW:
                    if shape == 2: circle(width-off,height-off,col,extra)
                    if shape == 3: trigon(width-(2*off),height-off,col,extra)
                    if shape == 4: square(width-off,height-(2*off),col,extra)
            else:
                (x,y) = slice_center(slice, layer)
                if shape == 2: circle(x,y,col,False)
                if shape == 3: trigon(x,y,col,False)
                if shape == 4: square(x,y,col,False)

    # possible moves
    letter = 65
    for (slice, layer) in possible_moves:
        if slice == -1:
            circle(cx,cy,BLACK,False,15)
            font.Draw(screen,None,24,chr(letter),(cx-6,cy-8),WHITE,'center','center',True)
        else:
            (x,y) = slice_center(slice, layer)
            circle(x,y,BLACK,False,15)
            font.Draw(screen,None,24,chr(letter),(x-6,y-8),WHITE,'center','center',True)
        letter += 1

    # order
    if players == 2: b = 35
    if players == 3: b = 55
    if players == 4: b = 75
    p = first_player
    for i in range(players):
        pg.draw.rect(screen, data[p][0], (cx-b+(mod_add(p,-first_player,players)*40),5,30,10))
        p = mod_add(p,1,players)


def occupied(layer, slice):
    for p in data:
        for piece in range(3):
            if p[piece+1][0] == layer and p[piece+1][1] == slice:
                return True
    return False

# direc is either, forward, back
def check_layer(layer, slice, shape, direc):
    moves = []
    if shape == -1: return []
    for sign in [1,-1]:
        new_slice = slice

        if mid_gate == slice:
            # inward through mid
            if layer == "out" and not occupied("mid", slice):
                if not direc == "back":
                    moves += check_layer("mid", slice, shape-1, "forward")
            # outward through mid
            if layer == "mid" and not occupied("out", slice):
                if not direc == "forward":
                    moves += check_layer("out", slice, shape-1, "back")
        if inn_gate == slice:
            # inward through inn
            if layer == "mid" and not occupied("inn", slice):
                if not direc == "back":
                    moves += check_layer("inn", slice, shape-1, "forward")
            # outward through inn
            if layer == "inn" and not occupied("mid", slice):
                if not direc == "forward":
                    moves += check_layer("mid", slice, shape-1, "back")
        if cen_gate == slice:
            if layer == "inn" and shape == 1:
                    moves += [(-1, "")]

        speed = shape
        while(speed > 0):
            new_slice = mod_add(new_slice, sign, slices)
            while(occupied(layer, new_slice)):
                new_slice = mod_add(new_slice, sign, slices)
            speed -= 1

            if mid_gate == new_slice:
                # inward through mid
                if layer == "out" and not occupied("mid", new_slice):
                    if not direc == "back":
                        moves += check_layer("mid", new_slice, speed-1, "forward")
                # outward through mid
                if layer == "mid" and not occupied("out", new_slice):
                    if not direc == "forward":
                        moves += check_layer("out", new_slice, speed-1, "back")
            if inn_gate == new_slice:
                # inward through inn
                if layer == "mid" and not occupied("inn", new_slice):
                    if not direc == "back":
                        moves += check_layer("inn", new_slice, speed-1, "forward")
                # outward through inn
                if layer == "inn" and not occupied("mid", new_slice):
                    if not direc == "forward":
                        moves += check_layer("mid", new_slice, speed-1, "back")
            if cen_gate == new_slice:
                if layer == "inn" and speed == 1:
                        moves += [(-1, "")]

        moves.append((new_slice,layer))
    return moves

def get_moves(piece):
    layer = data[current][piece+1][0]
    slice = data[current][piece+1][1]
    shape = piece+2
    if layer == "done": return []
    if layer == "dead":
        if occupied("out", 0): return []
        layer = "out"
        shape -= 1

    return list(set(check_layer(layer, slice, shape, "either")))

def do_move(i, piece):
    global first_player
    global last_player
    global current
    global possible_moves
    global win
    global old_data
    layer = possible_moves[i][1]
    slice = possible_moves[i][0]
    old_data = copy.deepcopy(data)
    if slice == -1: layer = "done"
    data[current][piece+1] = [layer, slice]
    if data[current][1][0] == data[current][2][0] == data[current][3][0] == "done":
        win = current
    if current == last_player:
        last_player = first_player
        first_player = mod_add(first_player, 1, players)
        current = -1
    else: current = mod_add(current, 1, players)
    possible_moves = []

sel = -1
while(1):
    for event in pg.event.get():
        if event.type == pg.QUIT: exit()
        if event.type == pg.KEYDOWN:
            if current < players:
                if event.key == ord('2'):
                    possible_moves = get_moves(0)
                    sel = 0
                if event.key == ord('3'):
                    possible_moves = get_moves(1)
                    sel = 1
                if event.key == ord('4'):
                    possible_moves = get_moves(2)
                    sel = 2
                if event.key == ord('u') and current != first_player:
                    current = mod_add(current,-1,players)
                    data = copy.deepcopy(old_data)
                    if sel != -1: possible_moves = get_moves(sel)
                if possible_moves != [] and sel != -1:
                    l = len(possible_moves)
                    if event.key - ord('a') >= 0 and event.key - ord('a') < l:
                        do_move(event.key - ord('a'), sel)
                        sel = -1

    clock.tick(10)
    screen.fill(BROWN)
    if win == -1: draw_board()
    else:
        if win == 0: print("Red wins!")
        if win == 1: print("Blue wins!")
        if win == 2: print("Green wins!")
        if win == 3: print("Yellow wins!")
        exit()
    pg.display.flip()
