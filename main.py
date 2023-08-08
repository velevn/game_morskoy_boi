import random


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self) -> str:
        print("Вы пытаетесь выстрелить за пределеы поля!")


class BoardUsedException(BoardException):
    def __str__(self) -> str:
        print("Вы уже стреляли в эту клетку!")


class BoardWrongShipException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class Ship:
    def __init__(self, bow, l, orientation):
        self.bow = bow
        # длина совпадает с количеством жизней
        self.len = l
        self.hp = l
        self.orientation = orientation

    # создаем координаты корабля

    @property
    def dot_ship(self):
        ship_dots = []
        for i in range(self.len):
            ship_x = self.bow.x
            ship_y = self.bow.y

            if self.orientation == 0:  # по горизонтали
                ship_x += i

            elif self.orientation == 1:  # по вертикали
                ship_y += i

            ship_dots.append(Dot(ship_x, ship_y))

        return ship_dots


class Board:
    def __init__(self, size=6, hid=False):
        self.size = size
        self.grid = [["O"]*size for _ in range(size)]
        self.ships = []
        self.busy = []  # занятые клетки

        self.hid = hid

        self.count = 0

    # генерируем доску
    def __str__(self):
        pole = ""
        pole += "    0 | 1 | 2 | 3 | 4 | 5"
        for row in range(self.size):
            pole += (f"\n"+str(row) + " | " + " | ".join(self.grid[row]))

        if self.hid:
            pole = pole.replace("■", "O")

        return pole

    # генерируем корабль
    def add_ships(self, ship):
        for d in ship.dot_ship:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dot_ship:
            self.grid[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    # рисуем контур корабля
    def contour(self, ship, verb=False):
        border = [(0, 1), (1, 1), (1, 0), (1, -1),
                  (0, -1), (-1, -1), (-1, 0), (-1, 1)]
        for d in ship.dot_ship:
            for dx, dy in border:
                dot_border = Dot(d.x+dx, d.y+dy)
                if not (self.out(dot_border)) and dot_border not in self.busy:
                    if verb:
                        self.grid[dot_border.x][dot_border.y] = "•"
                    self.busy.append(dot_border)

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    # выстрел
    def shot(self, d):
        if self.out(d):
            raise BoardOutException

        if d in self.busy:
            raise BoardUsedException

        self.busy.append(d)  # добавляем в список busy

        for ship in self.ships:
            if d in ship.dot_ship:
                ship.hp -= 1
                self.grid[d.x][d.y] = "X"
                if ship.hp == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return True
                else:
                    print("Корабль ранен!")
                    return True

        self.grid[d.x][d.y] == "•"
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()  # мeтод определен в наследуемом классе

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as error:
                print(error)


class User(Player):
    def ask(self):
        while True:
            coordinates = input("Ваш ход: ").split()

            if len(coordinates) != 2:
                print("Введите две координаты!")

            x, y = coordinates

            if not (x.isdigit()) or not (y.isdigit()):
                print("Введите числа!")

            x, y = int(x), int(y)

            return Dot(x, y)

class AI(Player):
    def ask(self):
        d = Dot(random.randint(0, 5), random.randint(0, 5))
        print(f"Компьютер ходит: {d.x} {d.y}")
        return d


class Game:
    def __init__(self, size=6):
        self.size = size
        self.hid = True
        pl = self.random_board()
        comp = self.random_board()
        comp.hid = False  # скрыть корабли компьютера

        self.user = User(pl, comp)
        self.ai = AI(comp, pl)
    # добавляем корабль на доску

    def random_board(self):
        board = None
        while board is None:
            board = self.place_ship()
        return board

    def place_ship(self):
        len_ship = [1]
        board = Board(size=self.size)
        count_attemp = 0  # счетчик попыток размещения кораблей

        for len in len_ship:
            while True:
                count_attemp += 1
                if count_attemp > 1000:
                    return None
                ship = Ship(Dot(random.randint(0, self.size-1),
                            (random.randint(0, self.size-1))), len, random.randint(0, 1))
                try:
                    board.add_ships(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        print("_"*40)
        print("|"+ " "*38+"|")
        print("| Добро пожаловать в игру Морской бой! |")
        print("|"+ "_"*38+"|")
        print(" ")

    def loop(self):
        num = 0
        while True:
            print("Поле пользователя:")
            print(self.user.board)
            print("_"*15)
            print(" ")
            print("Поле компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-"*20)
                print("Ходит пользователь:")
                repeat = self.user.move()
            else:
                print("Ходит компьютер:")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.user.board.count == 7:
                print("Компьютер выиграл!")
                break

            if self.ai.board.count == 7:
                print("Пользователь выиграл!")
                break

            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
