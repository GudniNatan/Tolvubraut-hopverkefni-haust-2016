# Gudni Natan Gunnarsson, 2016
import random


class Generator:
    def __init__(self):
        self.progress = 0
        self.generating = False
        self.done = False

    def getProgress(self):
        return self.progress

    def isDoneGenerating(self):
        return self.generating

    def reallyDone(self):
        self.generating = False
        self.done = True

    def isReallyDone(self):
        return self.done

    def regenerate(self, x, y, mx, my):
        self.generating = True
        self.done = False
        self.progress = 0
        return self.generate(x, y, mx, my)

    def generate(self, x, y, mx, my):
        if x >= mx-1:
            x = mx-1
        if y >= my-1:
            y = my-1
        maze = [[0 for i in range((my * 2) + 1)] for j in range((mx * 2) + 1)]
        visited = [[0 for i in range(my)] for j in range(mx)]
        totalSize = mx * my
        order = [[x, y]]
        moveNumber = 0
        visitedCount = 1
        for i in range(1, len(maze), 2):
            for j in range(1, len(maze[i]), 2):
                    maze[i][j] = 1
        while visitedCount < totalSize:     # Walk maze until every square is visited
            possibleSquares = [[1, 0], [0, 1], [-1, 0], [0, -1]]
            self.progress = (100 * moveNumber / (totalSize * 2)) + 1
            moveNumber += 1
            visited[x][y] = 1

            for move in list(possibleSquares):
                if x + move[0] < 0 or y + move[1] < 0 or x + move[0] == mx or y + move[1] == my:
                    possibleSquares.remove([move[0], move[1]])
                elif visited[x + move[0]][y + move[1]]:
                    possibleSquares.remove([move[0], move[1]])

            if len(possibleSquares) == 0:
                # Backtrack
                [x, y] = order[-2]
                order.pop()
            else:
                # Visit new square
                random.shuffle(possibleSquares)
                maze[(x * 2) + 1 + possibleSquares[0][0]][(y * 2) + 1 + possibleSquares[0][1]] = 1
                visitedCount += 1
                [x, y] = [x + possibleSquares[0][0], y + possibleSquares[0][1]]
                order.append([x, y])
        self.generating = True
        return maze
