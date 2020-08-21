import pygame
import tkinter as tk

import math

DEFAULT_SCREEN_SIZE = (1000, 800)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (245, 66, 66)
GRAY = (99, 107, 103)
GREEN = (15, 252, 3)
BLUE = (0,0,255)
PINK = (255,20,147)


GRID_LINE_WIDTH = 0.5

ROWS = 80
COLUMNS = 100

class Node:
    def __init__(self, r, c):
        self.parent = None
        self.neighbors = []
        self.r = r
        self.c = c

        self.f = 0
        self.g = 0
        self.h = 0

        self.closed = False

        self.blocked = False


    def path(self, color, surface):
        node_width = (surface.get_width() / COLUMNS) - (GRID_LINE_WIDTH)
        node_height = (surface.get_height() / ROWS) - (GRID_LINE_WIDTH)
        if not self.closed:
            pygame.draw.rect(surface, color, 
                                ((node_width + GRID_LINE_WIDTH) * self.c + GRID_LINE_WIDTH,
                                (node_width + GRID_LINE_WIDTH) * self.r + GRID_LINE_WIDTH,
                                node_width,
                                node_width))


    def show(self, color, surface):
        node_width = (surface.get_width() / COLUMNS) - (GRID_LINE_WIDTH)
        node_height = (surface.get_height() / ROWS) - (GRID_LINE_WIDTH)
        pygame.draw.rect(surface, color, 
                                ((node_width + GRID_LINE_WIDTH) * self.c + GRID_LINE_WIDTH,
                                (node_width + GRID_LINE_WIDTH) * self.r + GRID_LINE_WIDTH,
                                node_width,
                                node_height))


    
    def add_neighbors(self, board):
        r = self.r
        c = self.c

        directions = {(0, 1), (0, - 1), (1, 0), (-1, 0), (1, 1), (-1, 1), (1 , -1), (-1, -1)}

        directions_four_way = {(0, 1), (0, - 1), (1, 0), (-1, 0)}

        for r_d, c_d in directions_four_way:
            if 0 < r  < ROWS - 1 and 0 < c < COLUMNS - 1 and not board[r + r_d][c + c_d].blocked:
                self.neighbors.append(board[r + r_d][c + c_d])
        # #fix later
        # if r < ROWS - 1 and board[r + 1][c].blocked == False:
        #     self.neighbors.append(board[r + 1][c])

        # if r > 0 and board[r - 1][c].blocked == False:
        #     self.neighbors.append(board[r - 1][c])

        # if c < COLUMNS - 1 and board[r][c + 1].blocked == False:
        #     self.neighbors.append(board[r][c + 1])

        # if c > 0 and board[r][c - 1].blocked == False:
        #     self.neighbors.append(board[r][c - 1])



    def get_f(self):
        return self.f

    def get_g(self):
        return self.g

    def set_g(self, g):
        self.g = g

    def set_h(self, h):
        self.h = h

    def set_f(self):
        self.f = self.g + self.h

    def set_parent(self, parent):
        self.parent = parent

    def get_neighbors(self):
        return self.neighbors
        
class Pathfinder:
    def __init__(self, start, end, show_alg):
        self._board = [[Node(r,c) for c in range(COLUMNS)] for r in range(ROWS)]
        self._show_alg = show_alg
        self._path = []
        self._running = True

        self._start = self._board[int(start[0])][int(start[1])]
        self._end = self._board[int(end[0])][int(end[1])]

    def run(self):

        pygame.init()

        self._surface = pygame.display.set_mode(DEFAULT_SCREEN_SIZE)
        self._resize_surface(DEFAULT_SCREEN_SIZE)

        self._draw_board()

        while self._running:
            self._handle_events()

        pygame.quit()

    
    def _execute(self):
        #self._draw_board()

        self.astar()

        if len(self._path) > 0:
            for node in self._path:
                node.path(BLUE, self._surface)
            
            pygame.display.update()


    def _handle_events(self) -> None:
        '''
        Handle pygame events
        '''
        for event in pygame.event.get():
            self._handle_event(event)

    def _handle_event(self, event) -> None:
        '''
        Executing methods based on pygame events
        '''
        if event.type == pygame.QUIT:
            self._end_app()
        elif event.type == pygame.VIDEORESIZE:
            self._resize_surface(event.size)
        elif pygame.mouse.get_pressed()[0]:
            try:
                pos = pygame.mouse.get_pos()
                self._mouse_press(pos)
            except AttributeError:
                pass
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self._execute()


    def _mouse_press(self, pos):
        c = pos[0] // (DEFAULT_SCREEN_SIZE[0] // COLUMNS)
        r = pos[1] // (DEFAULT_SCREEN_SIZE[1] // ROWS)
        
        target = self._board[r][c]

        if target is not self._start and target is not self._end:
            if not target.blocked:
                target.blocked = True
                target.show(WHITE, self._surface)
            
        pygame.display.update()

    #algorithms
    def astar(self):
        open_list = [self._start]
        closed_list = []

        while(open_list):
            current_node = min(open_list, key=lambda node: node.get_f())
            print(current_node.r, current_node.c)
            open_list.remove(current_node)
            closed_list.append(current_node)

            #get path
            if current_node is self._end:
                current_path_node = current_node.parent
                while current_path_node != self._start:
                    current_path_node.closed = False
                    self._path.append(current_path_node)
                    current_path_node = current_path_node.parent
                
                return

            current_node.add_neighbors(self._board)
            
            for neighbor in current_node.get_neighbors():
                if neighbor not in closed_list:
                    temp_g = current_node.get_g() +self.heuristic_d(current_node, neighbor)
                    if neighbor in open_list:
                        if temp_g < neighbor.get_g():
                            neighbor.set_g(temp_g) 
                    else:
                        neighbor.set_g(temp_g)
                        open_list.append(neighbor)
                    
                    neighbor.set_h(self.heuristic_d(neighbor, self._end))
                    neighbor.set_f()

                if not neighbor.parent:
                    neighbor.set_parent(current_node)
                
            

            if self._show_alg:
                for node in open_list:
                    if node is not self._end:
                        node.show(GREEN, self._surface)

                for node in closed_list:
                    if node is not self._start:
                        node.show(RED, self._surface)

                pygame.display.update()

            current_node.closed = True


    def dijkstras(self):
        pass

    def _resize_surface(self, size: (int, int)) -> None:
        '''
        Resizing the screen
        @param size: tuple of 2 ints that would specify the new size of the screen
        '''
        self._surface = pygame.display.set_mode(size, pygame.RESIZABLE)
        self._surface.fill(GRAY)


    #drawing board
    def _draw_board(self) -> None:
        '''
        Drawing the entire playing field with the jewels and the various state indications
        '''

        for row in range(ROWS):
            for column in range(COLUMNS):
                if self._board[row][column] is self._start or self._board[row][column] is self._end:
                    self._board[row][column].show(PINK, self._surface)
                elif self._board[row][column].blocked:
                    self._board[row][column].show(WHITE, self._surface)
                else:
                    self._board[row][column].show(BLACK, self._surface)

        pygame.display.update()



    def heuristic_d(self, node1, node2):
        #return abs(node2.x - node1.x) + abs(node2.y - node1.y)
        return math.sqrt((node2.c - node1.c)** 2 + (node2.r - node1.r)** 2)
        #return min([abs(node2.x - node1.x), abs(node2.y - node1.y)])


    def _end_app(self) -> None:
        '''
        Ends the game by setting running to false
        '''
        self._running = False


class App(tk.Tk):
    def __init__(self, *args, **kargs):
        tk.Tk.__init__(self, *args, **kargs)
        frame = tk.Frame(self)
        frame.pack()
        label_start = tk.Label(frame, text="Start:")
        self.start_entry = tk.Entry(frame)
        label_end = tk.Label(frame, text="End:")
        self.end_entry = tk.Entry(frame)
        self.show_alg = tk.BooleanVar()
        self.show_alg_entry = tk.Checkbutton(frame, text= "Show Steps:", onvalue = True, offvalue = False, variable=self.show_alg)
        submit = tk.Button(frame, text="OK", command=self.on_submit)

        label_start.pack()
        self.start_entry.pack()
        label_end.pack()
        self.end_entry.pack()
        self.show_alg_entry.pack()
        submit.pack()

    def on_submit(self):
        start = self.start_entry.get().split(',')
        end = self.end_entry.get().split(',')

        Pathfinder(start, end, self.show_alg.get()).run()

if __name__ == "__main__":
    #Pathfinder().run()
    app = App()
    app.update()
    app.mainloop()