import pygame
import random

pygame.init()

screen = pygame.display.set_mode((800, 600))
screen_rect = screen.get_rect()

clock = pygame.time.Clock()
FPS = 50


def text_object(font, color, text):
    text_surf = font.render(text, True, color)
    return text_surf, text_surf.get_rect()


class Board:
    def __init__(self, dimension: int, mode: str, flag=None):
        """
        :param dimension: indicate dimension of board which is either 3 or 5 or 7
        :param mode: value either duo or ai
        :param flag: indicate ai mode hard or normal
        """
        self.dimension = dimension
        self.mode = mode
        self.flag = flag

        self.empty = '-'

        # generating a 2d list containing the play
        self.matrix = [[self.empty for _ in range(dimension)] for _ in range(dimension)]

        self.turn = 'o'  # the player x is to start the game

        # creating the board rectangle and positioning the board on the screen
        self.rect = pygame.Rect(0, 0, int(0.5 * screen_rect.width), int(0.5 * screen_rect.width))
        self.rect.bottom = screen_rect.bottom - 40
        self.rect.left = screen_rect.left + 40

        self.box_w = self.rect.width // self.dimension  # width of the box in the board
        self.rect.width = self.rect.height = self.box_w * self.dimension

        # players score
        self.x_score = 0
        self.o_score = 0

        self.pressed = True

        self.font = pygame.font.SysFont('Arial', self.box_w, True)

        if self.dimension > 7:
            self.num_of_times = 5
        elif self.dimension == 3:
            self.num_of_times = 3
        else:
            self.num_of_times = 4

        self.sub_lists = self.get_all_sub_list()

    def switch_turn(self):
        """
        switch turn of players on the board
        """
        if self.turn == 'o':
            self.turn = 'x'
        else:
            self.turn = 'o'

    def other_turn(self, turn):

        if turn == 'o':
            return 'x'
        return 'o'

    def num_from_index(self, row, col):
        """
        coverts index of box to box number
        :param row: the row position of the box
        :param col: the column position of the box
        :return: box number which range is from 1 -> dimension^2
        """
        return row * self.dimension + col + 1

    def index_from_num(self, num):
        """
        coverts box number to index of box
        :param num: the box number
        :return: a tuple containing row and col values
        """
        row = (num - 1) // self.dimension
        col = (num - 1) % self.dimension

        return row, col

    def is_valid_box(self, row, col):
        """
        :param row: the row position of the box
        :param col: the column position of the box
        :return: true if the box not played else false
        """
        return self.matrix[row][col] == self.empty

    def valid_boxes(self):
        """
        :return: list of un-played boxes in form of (row, col)
        """
        boxes = []
        for i in range(1, self.dimension ** 2 + 1):
            if self.is_valid_box(*self.index_from_num(i)):
                boxes.append(self.index_from_num(i))
        return boxes

    def index_from_mouse(self):
        """
        :return: a tuple containing row and col values
        """
        x, y = pygame.mouse.get_pos()
        if self.rect.collidepoint(x, y):
            row = (y - self.rect.top) // self.box_w
            col = (x - self.rect.left) // self.box_w
            try:
                _ = self.matrix[row][col]  # checking if index is in range
                return row, col
            except IndexError:
                return None

    def clicked(self):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(*pos):
            if pygame.mouse.get_pressed()[0]:
                if not self.pressed:
                    action = True
                    self.pressed = True
            else:
                self.pressed = False
        else:
            self.pressed = True
        return action

    def consecutive(self, sub_list, turn):

        assert len(sub_list) == self.num_of_times, "incorrect length of row"

        for i, j in sub_list:
            if self.matrix[i][j] != turn:
                return False
        return True

    def in_range(self, index1, index2):
        result = (0 <= index1 < self.dimension) and (0 <= index2 < self.dimension)
        return result

    def get_all_sub_list(self):
        sub_lists = []

        for row in range(self.dimension):
            for col in range(self.dimension):
                if self.in_range(row + self.num_of_times - 1, col + self.num_of_times - 1):
                    diagonal = []
                    for i in range(self.num_of_times):
                        diagonal.append((row + i, col + i))
                    sub_lists.append(diagonal)

                if self.in_range(row - self.num_of_times + 1, col + self.num_of_times - 1):
                    diagonal = []
                    for i in range(self.num_of_times):
                        diagonal.append((row - i, col + i))
                    sub_lists.append(diagonal)

                if self.in_range(row + self.num_of_times - 1, col):
                    vertical = []
                    for i in range(self.num_of_times):
                        vertical.append((row + i, col))
                    sub_lists.append(vertical)

                if self.in_range(row, col + self.num_of_times - 1):
                    horizontal = []
                    for i in range(self.num_of_times):
                        horizontal.append((row, col + i))
                    sub_lists.append(horizontal)

        random.shuffle(sub_lists)
        return sub_lists

    def check_win(self):
        for sub_list in self.sub_lists:
            if self.consecutive(sub_list, self.turn):
                return True, sub_list
        return False, None

    def game_end(self):
        return self.check_win()[0] or len(self.valid_boxes()) == 0

    def update_score(self):
        if self.check_win()[0]:
            if self.turn == 'x':
                self.x_score += 1
            else:
                self.o_score += 1
            print(self.x_score, self.o_score)
        else:
            self.switch_turn()

    def draw_grid(self):

        for i in range(0, self.dimension + 1):
            # drawing vertical lines
            pygame.draw.line(screen, "white", (self.rect.left + self.box_w * i, self.rect.top),
                             (self.rect.left + self.box_w * i, self.rect.bottom))

            # drawing horizontal lines
            pygame.draw.line(screen, "white", (self.rect.left, self.rect.top + self.box_w * i),
                             (self.rect.right, self.rect.top + self.box_w * i))

    def draw_board(self):
        # show mouse marker for validity
        index = self.index_from_mouse()
        if index and not self.check_win()[0]:
            row, col = index
            box = pygame.Rect(self.rect.left + col * self.box_w, self.rect.top + row * self.box_w, self.box_w,
                              self.box_w)
            pygame.draw.rect(screen, "green" if self.is_valid_box(row, col) else "red", box)

        # show contents of the board matrix
        for row, i in enumerate(self.matrix):
            for col, j in enumerate(i):
                box = pygame.Rect(self.rect.left + col * self.box_w, self.rect.top + row * self.box_w, self.box_w,
                                  self.box_w)
                if j != self.empty:
                    win, win_space = self.check_win()
                    if win:
                        pygame.draw.rect(screen, "green" if (row, col) in win_space else "red", box)
                    elif len(self.valid_boxes()) == 0:
                        pygame.draw.rect(screen, "red", box)
                    text_surf, text_rect = text_object(self.font, "white", j.upper())
                    text_rect.center = box.center
                    screen.blit(text_surf, text_rect)

    def draw(self):
        self.draw_board()
        self.draw_grid()

    def update(self):

        self.draw()
        if self.mode == "duo" and not self.game_end():
            if self.turn == 'x':
                if self.clicked():
                    index = self.index_from_mouse()
                    if index:
                        row, col = index
                        if self.is_valid_box(row, col):
                            self.matrix[row][col] = self.turn
                            self.update_score()
            else:
                self.ai_play('o')
                self.update_score()

    def complete(self, sub_list, turn):
        for k in range(len(sub_list)):
            i, j = sub_list[k]
            if self.matrix[i][j] == self.empty and \
                    (k == len(sub_list) - 1  or
                     self.matrix[sub_list[k + 1][0]][sub_list[k + 1][1]] != self.empty):
                self.matrix[i][j] = turn
                return

    def sub_list_count(self, sub_list, turn):
        count = 0

        for i, j in sub_list:
            if self.matrix[i][j] == turn:
                count += 1

        return count

    def sub_list_consecutive_count(self, sub_list, turn):
        forward_count = 0
        backward_count = 0

        for i, j in sub_list:
            if self.matrix[i][j] == turn:
                forward_count += 1
            elif self.matrix[i][j] == self.other_turn(turn):
                break

        for i, j in reversed(sub_list):
            if self.matrix[i][j] == turn:
                backward_count += 1
            elif self.matrix[i][j] == self.other_turn(turn):
                break

        return max(forward_count, backward_count)

    def sub_list_filled(self, sub_list):
        for i, j in sub_list:
            if self.matrix[i][j] == self.empty:
                return False
        return True

    def in_sub_list(self, sub_list, turn):
        for i, j in sub_list:
            if self.matrix[i][j] == turn:
                return True
        return False

    def ai_play(self, turn):
        random.shuffle(self.sub_lists)

        for sub_list in self.sub_lists:
            if self.sub_list_count(sub_list, turn) == self.num_of_times - 1:
                if not self.sub_list_filled(sub_list):
                    if self.sub_list_consecutive_count(sub_list, turn) == self.num_of_times - 1:
                        self.complete(sub_list, turn)
                        return

        for sub_list in self.sub_lists:
            if self.sub_list_count(sub_list, self.other_turn(turn)) == self.num_of_times - 1:
                if not self.sub_list_filled(sub_list):
                    if self.sub_list_consecutive_count(sub_list, self.other_turn(turn)) == self.num_of_times - 1:
                        self.complete(sub_list, turn)
                        return

        for sub_list in self.sub_lists:
            if self.sub_list_count(sub_list, self.other_turn(turn)) == self.num_of_times - 2:
                if not self.sub_list_filled(sub_list):
                    if self.sub_list_consecutive_count(sub_list, self.other_turn(turn)) == self.num_of_times - 2:
                        i1, j1 = sub_list[0]
                        i2, j2 = sub_list[-1]
                        if self.matrix[i1][j1] == self.empty and self.matrix[i2][j2] == self.empty:
                            self.complete(sub_list, turn)
                            return

        for i in range(self.num_of_times - 2, -1, -1):
            for sub_list in self.sub_lists:
                if self.sub_list_count(sub_list, turn) == i and not self.sub_list_filled(sub_list):
                    if self.sub_list_consecutive_count(sub_list, turn) == i \
                            and not self.in_sub_list(sub_list, self.other_turn(turn)):
                        self.complete(sub_list, turn)
                        return

        i, j = random.choice(self.valid_boxes())
        self.matrix[i][j] = turn

    def train_3x3(self):
        pass


def game(dimension: int, mode: str, flag=None):
    board = Board(dimension, mode, flag)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    break
                if event.key == pygame.K_r:
                    board.matrix = [[board.empty for _ in range(dimension)] for _ in range(dimension)]

        clock.tick(FPS)
        screen.fill("black")
        board.update()
        pygame.display.update()


if __name__ == '__main__':
    game(11,  "duo")
