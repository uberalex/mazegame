import pyxel
import math
import numpy as np
from random import randint

class App:
    def __init__(self):

        # CONSTS
        self.player_size = 4
        self.speed = 2
        self.box_size = 10
        self.grid_size = (24,24)
        self.offset = 8
        self.clip_size = (64, 64)
        self.clip_speed = [4,-4]

        pyxel.init(256,
                   256,
                caption='Maze Game')


        self.grid = np.random.randint(low=0, high=2, size=self.grid_size)
        self.clip_corner = [100, 100]
        self.player = {
                        'x' : pyxel.width / 2,
                        'y' : pyxel.height / 2,
                        'coord' : (0,0)
                }

        # test
        self.grid[11,11] = 2
        self.say_hello()
        pyxel.run(self.update, self.draw)

    def say_hello(self):
        print('hello');

    def update_player(self):

        if pyxel.btn(pyxel.KEY_LEFT):
            new_pos = max(self.player['x'] - self.speed,
                         (self.offset + 1))

            if self.can_move((new_pos, self.player['y'])):
                self.player['x'] = new_pos

        if pyxel.btn(pyxel.KEY_RIGHT):
            new_pos = min(self.player['x'] + self.speed, pyxel.width -
                         (self.player_size + self.offset + 1))


            if self.can_move((new_pos, self.player['y'])):
                self.player['x'] = new_pos


        if pyxel.btn(pyxel.KEY_UP):
            new_pos = max(self.player['y'] - self.speed,
                                  (self.offset + 1))



            if self.can_move((self.player['x'], new_pos)):
                self.player['y'] = new_pos

        if pyxel.btn(pyxel.KEY_DOWN):
            new_pos = min(self.player['y'] + self.speed, pyxel.height -
                (self.player_size + self.offset + 1))

            if self.can_move((self.player['x'], new_pos)):
                self.player['y'] = new_pos

        self.player['coord'] = self.calculate_coord((self.player['x'],
                                                    self.player['y']))

    def calculate_coord(self, coords):
        x_coord = ( (coords[0] - self.offset) // self.box_size)
        y_coord = ( (coords[1] - self.offset) // self.box_size)
        return (int(x_coord), int(y_coord))

    def can_move(self, coords):
        return self.grid[self.calculate_coord(coords)] != 1

    def check_win(self):
        return self.grid[self.calculate_coord((self.player['x'],self.player['y']))] == 2


    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        if not self.check_win():
            self.update_player()

    def draw_player(self):
        pyxel.rect(self.player['x'], self.player['y'], self.player['x'] + 4,
                self.player['y'] + 4, 10)

    def draw_grid(self):
        for col in range(self.grid_size[0]):
            for row in range(self.grid_size[1]):
                y_coord = self.offset  + row * self.box_size
                x_coord = self.offset  + col * self.box_size
                if self.grid[col, row] == 1:
                    pyxel.rect(x_coord, y_coord, x_coord + self.box_size,
                            y_coord + self.box_size, 5)
                if self.grid[col,row] == 2:
                    pyxel.circ(x_coord, y_coord, self.box_size/4, 8)
#               pyxel.rectb(x_coord, y_coord, x_coord + self.box_size, y_coord +
#                       self.box_size, 4)

    def draw_clip(self):
        pyxel.clip(self.clip_corner[0],
                   self.clip_corner[1],
                   self.clip_corner[0] + self.clip_size[0],
                   self.clip_corner[1] + self.clip_size[1])

        self.clip_corner[0] = np.clip(self.clip_corner[0] + self.clip_speed[0], 0, 256)
        self.clip_corner[1] = np.clip(self.clip_corner[1] + self.clip_speed[1], 0, 256)

        #check corners
        if self.clip_corner[0] <= 0 or (self.clip_corner[0] + self.clip_size[0]) >= 256:
            self.clip_speed[0] = -1 * np.sign(self.clip_speed[0]) * np.random.randint(low=2, high=6)

        if self.clip_corner[1] <= 0 or (self.clip_corner[1] + self.clip_size[1]) >= 256:
            self.clip_speed[1] = -1 * np.sign(self.clip_speed[1]) * np.random.randint(low=2, high=6)

    def draw_box(self, coords, mask):
        # 4 lsb for walls
        walls = mask & 15
        # north wall (1)
        if walls & 0b1 == 0b1:
            pyxel.line(coords[0], coords[1], coords[0] + self.box_size, coords[1], 12)
        # east wall (2)
        if walls & 0b10 == 0b10:
            pyxel.line(coords[0] + self.box_size, coords[1] + self.box_size, coords[0] + self.box_size, coords[1], 13)
        # west wall (4)
        if walls & 0b100 == 0b100:
            pyxel.line(coords[0], coords[1] + self.box_size, coords[0], coords[1], 14)
        # south wall (8)
        if walls & 0b1000 == 0b1000:
            pyxel.line(coords[0], coords[1] + self.box_size, coords[0] + self.box_size, coords[1] + self.box_size, 15)

        flags = mask >> 4
        pyxel.text(coords[0] +3, coords[1] + 2, "{}".format(str(flags)), 12)




    def draw(self):
        if self.check_win():
            pyxel.clip(0,0,256,256)
            pyxel.cls(5)
            pyxel.text(120, 80, "Winner!", pyxel.frame_count % 16)

        else:
            pyxel.cls(0)

            for i in range(1,25):
                for j in range(1,25):
                    self.draw_box((j*self.box_size, i*self.box_size),(15))
#            self.draw_grid()
            self.draw_player()
#            self.draw_clip()
        #pyxel.text(1,1,"({},{})".format(self.player['x'],self.player['y']), 3)
        #pyxel.text(100,1,"({},{})".format(
        #    self.player['coord'][0],
        #    self.player['coord'][1]),
        #    3)



if __name__=="__main__":
    App().draw_grid()
