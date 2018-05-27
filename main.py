import copy
import numpy as np

class Map:
    def __init__(self, dimention):
        "dimention is a length 2 array"
        self.dimention = dimention
        self.grid = [[[0, False]for i in range(dimention[0])] for j in range(dimention[1])]
        self.total_priority = 0

    def set_cell(self,position, value = [0,False]):
        self.grid[position[0]][position[1]] = value
        self.total_priority += value[0]

    def __str__(self):
        return ('\n'.join([''.join(['{:4}'.format(item[0]) for item in row])
                         for row in self.grid]))

class Camera:
    def __init__(self, position, orientation = 0):
        "0 = left, 1 = up, 2 = right, 3 = down"
        self.position = position
        self.orientation = orientation
    def __str__(self):
        return "[{}, {}]".format(self.position, self.orientation)

class State:
    def __init__(self, map, cameras):
        self.map = map
        self.cameras = cameras

    def move_camera(self, camera_num):
        new_cams = copy.deepcopy(self.cameras)
        position = new_cams[camera_num].position
        dimention = self.map.dimention
        if position[0] >= dimention[0] - 1:
            position[0] = 0
            position[1] += 1
            return State(self.map, new_cams)
        elif position[0] >= dimention[0] - 1 and position[1] >= dimention[1] - 1:
            #reached the end
            return 0
        else:
            position[0] += 1
            #print(*new_cams)
            return State(self.map, new_cams)

class Evaluator:
    def __init__(self):
        self.hi = "hi"

    def evaluate(self, state):
        current_best = [9999999,0]
        self.compute_min_achievement(copy.deepcopy(state.cameras), state.map, current_best)
        return current_best

    def compute_min_achievement(self, cameras, map, current_best, depth = 0):
        if depth >= len(cameras):
            achievement = self.compute_achievement(cameras, map)
            if achievement < current_best[0]:
                current_best = [achievement, copy.deepcopy(cameras)]
            #print(*cameras)

        else:
            while cameras[depth].orientation <= 3:
                new_cameras = copy.deepcopy(cameras)
                self.compute_min_achievement(new_cameras, map, current_best, depth + 1)
                cameras[depth].orientation += 1



    def compute_achievement(self, cameras, map):
        local_map = copy.deepcopy(map)
        achievement = 0
        for camera in cameras:
            self.camera_visibility_model(camera, local_map)
        for i in local_map.grid:
            for j in i:
                if j[0] > 0:
                    achievement += j[0]

        return achievement

    def camera_visibility_model(self, camera, map):
        temp_position = copy.deepcopy(camera.position)
        if  camera.orientation == 0:
            while temp_position[0] - 1  >= 0:
                map.grid[temp_position[0]-1][temp_position[1]][0] -=1
                temp_position[0] -= 1

        if  camera.orientation == 1:
            while temp_position[1] - 1  >= 0:
                map.grid[temp_position[0]][temp_position[1] -1][0] -=1
                temp_position[1] -= 1

        if  camera.orientation == 2:
            while temp_position[0] + 1  < len(map.grid) -1:
                map.grid[temp_position[0]+1][temp_position[1]][0] -=1
                temp_position[0] += 1

        if  camera.orientation == 3:
            while temp_position[1] + 1  < len(map.grid[0]) -1:
                map.grid[temp_position[0]][temp_position[1] -1][0] -=1
                temp_position[1] += 1
        # print(camera, map)
class BFS:
    def __init__(self, map, cameras):
        self.best_achievement = map.total_priority
        self.best_setup = cameras
        self.cameras = cameras
        self.map = map
    #BFS with stack
    def start_bfs(self):
        inistate = State(self.map, self.cameras)
        stack = []
        stack.insert(0, inistate)
        evaluator = Evaluator()
        while len(stack) > 0:
            current = stack.pop()
            result = evaluator.evaluate(current)
            if result[0] < self.best_achievement:
                current.minAchievement = result[0]
                current.bestSetup = result[1]
            for index, camera in enumerate(self.cameras):
                nextState = current.move_camera(index)
                if nextState != 0:
                    stack.insert(0, nextState)
        print('bfs complete!')
        return [self.best_achievement, self.best_setup]
def Test():
    print("1234")

    cameras = [Camera([0, 0]),Camera([0, 0]),Camera([0, 0]),Camera([0, 0])]

    evaluator = Evaluator()
    evaluator.compute_min_achievement(cameras, None,0)

def main():
    map = Map([3,3])
    map.set_cell([1,2],[1,False])
    cameras = [Camera([0,0]), Camera([0,0])]
    # state = State(map,cameras)



    bfs = BFS(map,cameras)
    result = bfs.start_bfs()
    print(result[0])
    print(map)

if __name__ == '__main__':
    main()