import pyxel
import math
import numpy as np
from   random import randint
import random

class Maze:
    def __init__(self, gridsize):
        # Compass
        self.north = 0b1
        self.east  = 0b10
        self.south = 0b100
        self.west  = 0b1000
        self.opposites  = {
            self.north : self.south,
            self.south : self.north,
            self.west  : self.east,
            self.east  : self.west,
        }
        self.dx = { self.east : 1, self.west : -1, self.north : 0, self.south : 0 }
        self.dy = { self.east : 0, self.west :  0, self.north : -1, self.south : 1 }

        self.grid = np.zeros(gridsize, dtype=int)

    def carve_passage(self, start_coords):
        directions = [self.north, self.south, self.east, self.west]
        random.shuffle(directions)

        for direction in directions:
            new_coords = (start_coords[0] + self.dx[direction], start_coords[1] + self.dy[direction])

            if (0 <= new_coords[0] < len(self.grid) ) and (0 <= new_coords[1] < len(self.grid[0])) and (self.grid[new_coords] == 0):
                self.grid[start_coords] |= direction
                self.grid[new_coords]   |= self.opposites[direction]

                self.carve_passage(new_coords)


    def print_maze(self):
        print(self.grid)

class App:
    def __init__(self):

        # CONSTS
        self.player_size = 2
        self.speed = 2
        self.box_size = 10
        self.grid_size = (10,10)
        self.clip_size = (self.grid_size[0]*self.box_size//2,
                          self.grid_size[1]*self.box_size//2)
        self.clip_speed = [4,-4]

        # Compass
        self.north = 0b1
        self.east  = 0b10
        self.south = 0b100
        self.west  = 0b1000
        self.opposites  = {
            self.north : self.south,
            self.south : self.north,
            self.west  : self.east,
            self.east  : self.west,
        }
        #hack to get the right and bottom lines to draw
        self.border = 6

        pyxel.init(self.grid_size[0]*(self.box_size)+self.border, self.grid_size[1]*(self.box_size)+self.border, caption='Maze Game')
        print(pyxel.width,pyxel.height)

        #self.grid = np.random.randint(low=0, high=8, size=self.grid_size)
        #self.grid = np.full(self.grid_size, self.north|self.west)
        m = Maze(self.grid_size)
        m.carve_passage((0,0))
        # the grid is a path, need to invert it to make walls
        self.grid = (~m.grid & 15).copy()
        #self.grid = np.zeros(self.grid_size, dtype=int)
        # add outer walls
        self.grid[0]    |= self.west
        self.grid[-1]   |= self.east
        self.grid[:,-1] |= self.south
        self.grid[:,0]  |= self.north
        print(self.grid)
        self.clip_corner = [100, 100]
        self.player = {
        'x' : self.player_size,
        'y' : self.player_size,
        'coord' : (0,0)
        }

        self.grid[random.randint(0,len(self.grid)-1), random.randint(0,len(self.grid[0])-1)] |= 2 << 4

        # test
        pyxel.run(self.update, self.draw)

    def update_player(self):

        from_coords = (self.player['x'], self.player['y'])

        if pyxel.btn(pyxel.KEY_LEFT):
            new_pos = max(self.player['x'] - self.speed, (self.player_size))

            if self.can_move(from_coords, (new_pos, self.player['y']), self.west):
                self.player['x'] = new_pos

        if pyxel.btn(pyxel.KEY_RIGHT):
            # need to add border to draw the right-most line
            new_pos = min(self.player['x'] + self.speed, pyxel.width - (self.border + self.player_size))

            if self.can_move(from_coords, (new_pos, self.player['y']), self.east):
                self.player['x'] = new_pos


        if pyxel.btn(pyxel.KEY_UP):
            new_pos = max(self.player['y'] - self.speed, self.player_size)

            if self.can_move(from_coords, (self.player['x'], new_pos), self.north):
                self.player['y'] = new_pos

        if pyxel.btn(pyxel.KEY_DOWN):
            new_pos = min(self.player['y'] + self.speed, pyxel.height - (self.border + self.player_size))

            if self.can_move(from_coords, (self.player['x'], new_pos), self.south):
                self.player['y'] = new_pos

        self.player['coord'] = self.calculate_coord((self.player['x'], self.player['y']))

    def calculate_coord(self, coords):
        x_coord = min(( (coords[0]) // self.box_size), self.grid_size[0]-1)
        y_coord = min(( (coords[1]) // self.box_size), self.grid_size[1]-1)
        return (int(x_coord), int(y_coord))

    def can_move(self, from_coords, to_coords, direction):
        origin = self.calculate_coord(from_coords)
        origin_walls = self.grid[origin]
        dest = self.calculate_coord(to_coords)
        dest_walls = self.grid[dest]

        if origin != dest:
            if (direction & origin_walls == direction) or (self.opposites[direction] & dest_walls == self.opposites[direction]):
                return False
            else:
                return True
        else:
            return True


    def check_win(self):
        return self.grid[self.calculate_coord((self.player['x'],self.player['y']))] >> 4 == 2


    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        if not self.check_win():
            self.update_player()

    def draw_player(self):
        pyxel.rect(self.player['x'] - (self.player_size),
                   self.player['y'] - (self.player_size),
                   self.player['x'] + (self.player_size),
                   self.player['y'] + (self.player_size), 10)
        #dot in the middle
        pyxel.rect(self.player['x'],
                   self.player['y'],
                   self.player['x'],
                   self.player['y'], 1)

    def draw_grid(self):

        for col in range(self.grid_size[0]):
            for row in range(self.grid_size[1]):
                y_coord = row * self.box_size
                x_coord = col + self.box_size

                if self.grid[col, row] == 1:
                    pyxel.rect(x_coord, y_coord, x_coord + self.box_size, y_coord + self.box_size, 5)
                if self.grid[col,row] == 2:
                    pyxel.circ(x_coord, y_coord, self.box_size/4, 8)

                pyxel.rectb(x_coord, y_coord, x_coord + self.box_size, y_coord + self.box_size, 4)

    def draw_clip(self):
        pyxel.clip(self.clip_corner[0],
        self.clip_corner[1],
        self.clip_corner[0] + self.clip_size[0],
        self.clip_corner[1] + self.clip_size[1])

        self.clip_corner[0] = np.clip(self.clip_corner[0] + self.clip_speed[0], -self.clip_size[0], pyxel.width)
        self.clip_corner[1] = np.clip(self.clip_corner[1] + self.clip_speed[1], -self.clip_size[1], pyxel.height)

        #check corners
        if (self.clip_corner[0] <= -self.clip_size[0]) or (self.clip_corner[0] + self.clip_size[0]) >= pyxel.width + self.clip_size[0]:
            self.clip_speed[0] = -1 * np.sign(self.clip_speed[0]) * np.random.randint(low=2, high=6)

        if (self.clip_corner[1] <= -self.clip_size[1]) or (self.clip_corner[1] + self.clip_size[1]) >= pyxel.height + self.clip_size[1]:
            self.clip_speed[1] = -1 * np.sign(self.clip_speed[1]) * np.random.randint(low=2, high=6)

    def draw_box(self, coords, mask):
        # 4 lsb for walls
        walls = mask & 15
        # north wall (1)
        if walls & self.north == self.north:
            pyxel.line(coords[0], coords[1], coords[0] + self.box_size, coords[1], 12)
        # east wall (2)
        if walls & self.east == self.east:
            pyxel.line(coords[0] + self.box_size, coords[1] + self.box_size, coords[0] + self.box_size, coords[1], 12)
        # west wall (8)
        if walls & self.west == self.west:
            pyxel.line(coords[0], coords[1] + self.box_size, coords[0], coords[1], 12)
        # south wall (4)
        if walls & self.south:
            pyxel.line(coords[0], coords[1] + self.box_size, coords[0] + self.box_size, coords[1] + self.box_size, 12)

        flags = mask >> 4
        if flags == 2:
            pyxel.text(coords[0] + 2, coords[1] + 2, "@", 14)
        #pyxel.text(coords[0]+2,coords[1]+2, "{}".format(self.grid[self.calculate_coord(coords)]), 12)

    def draw(self):
        if self.check_win():
            pyxel.clip(0,0,pyxel.width,pyxel.height)
            pyxel.cls(5)
            pyxel.text(pyxel.width//3+6, pyxel.height//2, "Winner!", pyxel.frame_count % 16)

        else:
            pyxel.cls(0)
            for i in range(self.grid_size[0]):
                for j in range(self.grid_size[1]):
                    self.draw_box((j*self.box_size, i*self.box_size),
                                  (self.grid[self.calculate_coord((j*self.box_size, i*self.box_size))]))

            self.draw_player()
            self.draw_clip()
        #pyxel.text(1,1,"({},{})".format(self.player['x'],self.player['y']), 3)
        #pyxel.text(100,1,"({},{})".format(self.player['coord'][0],   self.player['coord'][1]), 3)



if __name__=="__main__":
    App()
