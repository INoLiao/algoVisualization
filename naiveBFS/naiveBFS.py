import tkinter
import time
from enum import Enum
from collections import deque
from PIL import Image, ImageTk

# Status of path searching.
class Status(Enum):
    START = 1
    END = 2
    EMPTY = 3
    WALL = 4
    VISITED = 5
    PATH = 6

# GUI Concole.
class Console:

    # @param title: str
    # @param size: Tuple(int, int)
    def __init__(self, title, windowSize):

        # initialize window
        self.window = tkinter.Tk()
        self.window.title = title
        self.window.geometry(f'{windowSize[0]}x{windowSize[1]}')

        # initialize canvas
        self.canvas = tkinter.Canvas(self.window)
        self.canvas.configure(bg = "black")
        self.canvas.pack(fill = "both", expand = True)

        # members
        self.windowSize = windowSize
        self.running = True
        self.images = []

    # Draw the board on canvas.
    # @param board: List[List[Status]]
    def drawBoard(self, board):
        self.canvas.delete("all")
        m, n = len(board), len(board[0])
        width, height = self.windowSize[0] // n, self.windowSize[1] // m
        for row in range(m):
            for col in range(n):
                row0, col0 = row * height, col * width
                color = self.getColor(board[row][col])
                self.canvas.create_rectangle(col0, row0, col0 + width, row0 + height, fill = color, outline="white")

    # Draw path over the existing board.
    # @param board: List[List[Status]]
    # @param path: Tuple(Tuple(int, int), PhotoImage)
    def drawPath(self, board, path):
        m, n = len(board), len(board[0])
        width, height = self.windowSize[0] // n, self.windowSize[1] // m
        for coordinate, image in path:
            row0, col0 = coordinate[0] * height, coordinate[1] * width
            if image == "up":
                self.images.append(upArrow.getImage((width, height)))
            elif image == "down":
                self.images.append(downArrow.getImage((width, height)))
            elif image == "left":
                self.images.append(leftArrow.getImage((width, height)))
            elif image == "right":
                self.images.append(rightArrow.getImage((width, height)))
            self.canvas.create_image(col0, row0, image = self.images[-1], anchor = "nw")

    # Exit GUI.
    def exit(self):
        self.running = False
        print("Window cloased")

    # @param value: int
    # @return str
    def getColor(self, value):
        if value == Status.START:
            return "darkblue"
        elif value == Status.END:
            return "darkred"
        elif value == Status.EMPTY:
            return "gray"
        elif value == Status.WALL:
            return "black"
        elif value == Status.VISITED:
            return "orange"
        elif value == Status.PATH:
            return "green"

# 2D Board.
class Board:

    # @param List[List[int]]
    # @return None
    def __init__(self, board):
        self.board = board

    # @return List[List[int]]
    def getBoard(self):
        return self.board

# Graph Utility.
class Graph:
    
    def __init__(self, console, window):
        self.console = console
        self.window = window

    def updateGUI(self, board):
        self.console.drawBoard(board)
        self.window.update()

    def drawPath(self, board, path):
        self.console.drawPath(board, path)
        self.window.update()

    # @param board: List[List[Status]]
    # @param start: Tuple(int, int)
    # @param end: Tuple(int, int)
    def findShortestPath(self, board, start, end):

        # initialize
        queue = deque()
        queue.append(start)
        predecessor = {}
        predecessor[start] = -1

        # BFS
        while queue and self.console.running:

            # visit
            node = queue.popleft()
            if node == end:
                self.updateBoardWithPath(board, predecessor, node)
                self.updateGUI(board)
                self.drawPath(board, self.derivePath(predecessor, node))
                return True

            # mark as visited
            if node != start:
                board[node[0]][node[1]] = Status.VISITED

            # update GUI
            self.updateGUI(board)

            # explore neighbors
            for neighbor in self.findNeighbors(board, node):
                if neighbor not in predecessor:
                    predecessor[neighbor] = node
                    queue.append(neighbor)

        return False

    # Find neighbors of the node.
    # @param board: List[List[Status]]
    # @param node: Tuple(int, int)
    # @return List[Tuple(int, int)]
    def findNeighbors(self, board, node):

        # initialize
        i, j = node[0], node[1]
        neighbors = []

        # find neighbors
        for x, y in [(i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)]:
            if 0 <= x < len(board) and 0 <= y < len(board[0]):
                if board[x][y] != Status.WALL:
                    neighbors.append((x, y))

        return neighbors

    # Draw the shortest path on the board.
    # @param board: List[List[Status]]
    # @param predecessor: dict({ Tuple(int, int): Tuple(int, int) })
    # @param node: Tuple(int, int)
    # @return List[List[Status]]
    def updateBoardWithPath(self, board, predecessor, node):

        # move one step (to keep the mark of end node)
        node = predecessor[node]

        # mark the path
        while predecessor[node] != -1:
            board[node[0]][node[1]] = Status.PATH
            node = predecessor[node]

        return board

    # Derive the path with direction.
    # @param predecessor: dict({ Tuple(int, int): Tuple(int, int) })
    # @param node: Tuple(int, int)
    # @return List[Tuple(Tuple(int, int), str)]
    def derivePath(self, predecessor, node):

        # initialize
        path = []
        direction = self.deriveDirection(predecessor[node], node)
        node = predecessor[node]

        while predecessor[node] != -1:

            # current node
            path.append((node, direction))

            # previous node
            direction = self.deriveDirection(predecessor[node], node)
            node = predecessor[node]

        return path

    # Derive the direction from start node to end node.
    # @param start: Tuple(int, int)
    # @param end: Tuple(int, int)
    # @return List[Tuple(Tuple(int, int), str)]
    def deriveDirection(self, start, end):
        if start[0] + 1 == end[0]:
            return "down"
        elif start[0] - 1 == end[0]:
            return "up"
        elif start[1] + 1 == end[1]:
            return "right"
        elif start[1] - 1 == end[1]:
            return "left"
        else:
            raise Exception("Invalid input: start and end should be neighbors to each other")

# Image utility class.
class ImageUtil:

    # @param filePath: str
    def __init__(self, filePath):
        self.image = Image.open(filePath)

    # @param size: Tuple(int, int)
    # @return 
    def getImage(self, size):
        self.image = self.image.resize(size)
        return ImageTk.PhotoImage(self.image)

if __name__ == '__main__':

    # Initialize console
    console = Console("2D Grid", (800, 800))

    # Initialize board
    board = Board([[Status.EMPTY] * 20 for _ in range(20)])
    start, end = (2, 2), (17, 11)
    board.board[start[0]][start[1]] = Status.START
    board.board[end[0]][end[1]] = Status.END

    # Draw walls
    count = 0
    for i in range(4, 15, 2):
        for j in range(count, 15 + count, 1):
            board.board[i][j] = Status.WALL
        count += 1
    for i in range(16, 20):
        board.board[i][9] = Status.WALL
    for j in range(10, 12):
        board.board[16][j] = Status.WALL
    for i in range(16, 19):
        board.board[i][12] = Status.WALL


    # Initialize image
    upArrow = ImageUtil("up.png")
    downArrow = ImageUtil("down.png")
    leftArrow = ImageUtil("left.png")
    rightArrow = ImageUtil("right.png")

    # Set window
    window = console.window
    window.protocol("WM_DELETE_WINDOW", console.exit)

    # Start the animation
    graph = Graph(console, window)
    time.sleep(5)
    graph.findShortestPath(board.getBoard(), start, end)

    # Animation finishes
    while console.running:
        window.update()
        time.sleep(0.1)
