import copy
# import numpy as np
import time


class Map:
    def __init__(self, dimention):
        "dimention is a length 2 array"
        self.dimention = dimention
        self.grid = [[[0, False]for i in range(dimention[0])] for j in range(dimention[1])]
        self.total_priority = 0

    def set_cell(self, position, value=[0, False]):
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
    #next state is defined by moving 1 camera by 1 position
    def move_camera(self, camera_num):
        new_cams = copy.deepcopy(self.cameras)
        position = new_cams[camera_num].position
        dimention = self.map.dimention

        if position[0] == dimention[0] - 1 and position[1] == dimention[1] - 1:
            #reached the end
            return 0
        elif position[0] >= dimention[0] - 1:
            position[0] = 0
            position[1] += 1
            # print(*new_cams)
            return State(self.map, new_cams)
        else:
            position[0] += 1
            # print(*new_cams)
            return State(self.map, new_cams)

#evaluate the achievement of 1 state
class Evaluator:
    def __init__(self):
        self.hi = "hi"

    def evaluate(self, state):
        current_best = [9999999,0]
        value = self.compute_min_achievement(copy.deepcopy(state.cameras), state.map, current_best)
        return value

    #compute achievement for all possible camera orientation setup and find minimum achievement
    def compute_min_achievement(self, cameras, map, current_best, depth = 0):
        if depth >= len(cameras):

            achievement = self.compute_achievement(cameras, map)
            #print(*cameras)

            if achievement < current_best[0]:
                return [achievement, copy.deepcopy(cameras)]



        else:
            temp = current_best
            while cameras[depth].orientation <= 3:
                new_cameras = copy.deepcopy(cameras)
                ach = self.compute_min_achievement(new_cameras, map, current_best, depth + 1)
                if ach[0] < temp[0]:
                    temp = ach
                cameras[depth].orientation += 1
            return temp


    #computed achievement for 1 camera orientation setup
    def compute_achievement(self, cameras, map):
        local_map = copy.deepcopy(map)
        achievement = 0
        # print(local_map)
        for camera in cameras:
            self.camera_visibility_model(camera, local_map)

        # print(local_map)
        for i in local_map.grid:
            for j in i:
                if j[0] > 0:
                    achievement += j[0]

        return achievement

    #visibility model for camera, currently assume that a camera will look straitght as far as it can until it reaches a wall
    def camera_visibility_model(self, camera, map):
        temp_position = copy.deepcopy(camera.position)
        if camera.orientation == 0:
            while temp_position[0] - 1 >= 0:
                if map.grid[temp_position[0]-1][temp_position[1]][1] :
                    return
                map.grid[temp_position[0]-1][temp_position[1]][0] -=1
                temp_position[0] -= 1

        if  camera.orientation == 1:
            while temp_position[1] - 1 >= 0:
                if map.grid[temp_position[0]][temp_position[1] -1][1] :
                    return
                map.grid[temp_position[0]][temp_position[1] -1][0] -=1
                temp_position[1] -= 1

        if  camera.orientation == 2:
            while temp_position[0] + 1 <= len(map.grid) -1:
                if map.grid[temp_position[0]+1][temp_position[1]][1] :
                    return
                map.grid[temp_position[0]+1][temp_position[1]][0] -=1
                temp_position[0] += 1

        if  camera.orientation == 3:
            while temp_position[1] + 1  <= len(map.grid[0]) -1:
                if map.grid[temp_position[0]][temp_position[1] +1][1] :
                    return
                map.grid[temp_position[0]][temp_position[1] +1][0] -=1
                temp_position[1] += 1
        # print(camera, map)

class BeamSearchQueue:
    def __init__(self, size):
        self.size = size
        self.priorityQueue = []
        self.dict = {}

    def push(self, state, achievement):
        key = ""
        for camera in state.cameras:
            key += ''.join(str(x) for x in camera.position)
            key += ':'
        if key in self.dict:
            return
        else:
            self.dict.update({key: state})
            self.queue.insert(0, state)


#a unique queue that doesnt allow duplicate states
class UniqueCameraQueue:
    def __init__(self):
        self.queue = []
        self.dict = {}

    def push(self, state):
        key = ""
        for camera in state.cameras:
            key += ''.join(str(x) for x in camera.position)
            key += ':'
        if key in self.dict:
            return
        else:
            self.dict.update({key: state})
            self.queue.insert(0, state)
    def length(self):
        return len(self.queue)

    def pop(self):
        state = self.queue.pop()
        key = ""
        for camera in state.cameras:
            key += ''.join(str(x) for x in camera.position)
            key += ':'
        self.dict.pop(key)
        return state



#bfs with unique queue
class BFSWithNonDupQueue:
    def __init__(self, map, cameras):
        self.best_achievement = map.total_priority
        self.best_setup = cameras
        self.cameras = cameras
        self.map = map
    #BFS with stack
    def start_bfs(self):
        inistate = State(self.map, self.cameras)
        queue = UniqueCameraQueue()
        queue.push(inistate)
        evaluator = Evaluator()
        printThreshold = 0
        while queue.length() > 0:

            if queue.length() > printThreshold:
                printThreshold += 100
                print("queue lenghth: " + str(queue.length()))
            current = queue.pop()
            # print("12345111111111111111111111111111111111111111111111111111111111111111111111111111111")
            # print('\n'.join([''.join([str(camera) for camera in state.cameras])
            #              for state in stack]))
            # print("Parent:" + str(' '.join(str(camera) for camera in current.cameras)))

            result = evaluator.evaluate(current)
            if result[0] == 0:
                return result

            if result[0] < self.best_achievement:
                self.best_achievement = result[0]
                self.best_setup = result[1]
                print("new best: " + str(self.best_achievement))
            for i in range(0, len(self.cameras)):
                nextState = current.move_camera(i)

                if nextState != 0:
                    queue.push(nextState)
                    # print("Child:" + str(' '.join(str(camera) for camera in nextState.cameras)))
                if nextState == 0:
                    # print(len(stack))
                    pass
        print('bfs complete!')
        return [self.best_achievement, self.best_setup]

class DFS:
    def __init__(self, map, cameras):
        self.best_achievement = map.total_priority
        self.best_setup = cameras
        self.cameras = cameras
        self.map = map
        self.visited_dict = {}

    def start(self):
        init_state = State(self.map, self.cameras)
        stack = []
        stack.append(init_state)
        eval = Evaluator()
        current_state = init_state
        camera_num = 0

        traceback = False
        traceback_camera_num = 0

        while len(stack) > 0:
            while True:
                # not re-evaluate when tracing back from next node
                next_state = None
                if not traceback:
                    result = eval.evaluate(current_state)
                    if result[0] == 0:
                        return result

                    if result[0] < self.best_achievement:
                        self.best_achievement = result[0]
                        self.best_setup = result[1]

                    self.visited_dict[self.get_key(current_state)] = True
                    next_state = current_state.move_camera(camera_num)
                else:
                    # find if any node is not yet traversed
                    for i in range(0, len(self.cameras)):
                        next_state = current_state.move_camera(i)
                        if next_state != 0 and self.get_key(next_state) not in self.visited_dict:
                            camera_num = i
                            traceback = False
                            break

                if next_state == 0 or traceback is True:
                    # print("###########################Trace back by 1 #####################################")
                    current_state = stack.pop()
                    traceback = True
                    # print("Pop node:" + str(' '.join(str(camera) for camera in current_state.cameras)))
                    break
                else:
                    # print("Pushing Child:" + str(' '.join(str(camera) for camera in next_state.cameras)))
                    stack.append(next_state)
                    current_state = next_state

    def get_key(self, state):
        key = ''
        for camera in state.cameras:
            key += ''.join(str(x) for x in camera.position)
            key += ':'
        return key



# classic bfs with queue
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
            # print("12345111111111111111111111111111111111111111111111111111111111111111111111111111111")
            # print('\n'.join([''.join([str(camera) for camera in state.cameras])
            #              for state in stack]))
            # print("Parent:" + str(' '.join(str(camera) for camera in current.cameras)))

            result = evaluator.evaluate(current)
            if result[0] == 0:
                return result

            if result[0] < self.best_achievement:
                self.best_achievement = result[0]
                self.best_setup = result[1]
            for i in range(0, len(self.cameras)):
                nextState = current.move_camera(i)
                # p
                if nextState != 0:
                    stack.insert(0, nextState)
                    # print("Child:" + str(' '.join(str(camera) for camera in nextState.cameras)))
                if nextState == 0:
                    # print(len(stack))
                    pass
        print('bfs complete!')
        return [self.best_achievement, self.best_setup]


def Test():
    print("1234")

    cameras = [Camera([0, 0]),Camera([0, 0]),Camera([0, 0]),Camera([0, 0])]

    evaluator = Evaluator()
    evaluator.compute_min_achievement(cameras, None,0)

def main():
    #initialize map
    test1()

def test1():
    map = Map([5, 5])
    map.set_cell([1, 1], [1, False])
    map.set_cell([2, 2], [1, False])
    map.set_cell([3, 3], [1, False])
    # map.set_cell([4, 6], [0, True])
    # map.set_cell([4, 4], [1, False])
    # map.set_cell([2, 3], [1, False])
    # map.set_cell([4, 7], [1, False])
    # map.set_cell([2, 2], [1, False])
    # map.set_cell([3, 3], [1, False])
    # map.set_cell([4, 3], [1, False])
    # initialize camera
    cameras = [Camera([0, 0], 0), Camera([0, 0], 0),Camera([0, 0], 0)]

    # bfs = BFSWithNonDupQueue(map, cameras)
    # result = bfs.start_bfs()
    # print(result[0])
    # print(*result[1])

    dfs = DFS(map, cameras)
    result = dfs.start()
    print(result[0])
    print(*result[1])


if __name__ == '__main__':
    start = time.time()
    main()
    end = time.time()
    print(str((end - start)/60 ) + " min")