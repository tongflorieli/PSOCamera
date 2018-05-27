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
        self.valid_direction = []
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
        local_cam = copy.deepcopy(state.cameras)
        self.check_valid_direction(local_cam, state.map)
        local_cam = [cam for cam in local_cam if len(cam.valid_direction) > 0]
        local_cam = self.filter_same_position(local_cam)
        if len(local_cam)> 0:
            current_best = self.compute_min_achievement(local_cam, state.map, current_best)
        return current_best

    def filter_same_position(self, cameras):
        output = []
        seen = set()
        for camera in cameras:
            key = ''.join(str(x) for x in camera.position)
            if key not in seen:
                output.append(camera)
                seen.add(key)
        return output

    def check_valid_direction(self, cameras, map):

        # print(local_map)
        for camera in cameras:
            while camera.orientation < 4:
                local_map = copy.deepcopy(map)
                achievement = 0
                self.camera_visibility_model(camera, local_map)
                for i in local_map.grid:
                    for j in i:
                        if j[0] > 0:
                            achievement += j[0]
                if achievement < map.total_priority:
                    camera.valid_direction.insert(0,camera.orientation)
                camera.orientation +=1
            #reset orientation
            camera.orientation = 0
        #print(*cameras)


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
        self.queue = []
        self.dict = {}

    def __keygen(self, cameras):
        key = ""
        for camera in cameras:
            key += ''.join(str(x) for x in camera.position)
            key += ':'
        return key

    def push(self, state, achievement):
        key = ""
        for camera in state.cameras:
            key += ''.join(str(x) for x in camera.position)
            key += ':'
        if key in self.dict:
            return
        else:
            self.dict.update({key: state})
            self.queue.insert(0, (achievement,state))
            if len(self.queue) > self.size:
                maxLocation = self.queue.index(max(self.queue, key=lambda x: x[0]))
                maxState = self.queue.pop(maxLocation)[1]
                newKey = self.__keygen(maxState.cameras)
                self.dict.pop(newKey)
    def pop(self):
        state = self.queue.pop()[1]
        key = ""
        for camera in state.cameras:
            key += ''.join(str(x) for x in camera.position)
            key += ':'
        self.dict.pop(key)
        return state
    def length(self):
        return len(self.queue)


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

#Beam Search
class BeamSearch:
    def __init__(self, map, cameras, beam_width):
        self.best_achievement = map.total_priority
        self.best_setup = cameras
        self.cameras = cameras
        self.map = map
        self.width = beam_width

    def start_bfs(self):
        inistate = State(self.map, self.cameras)
        queue = BeamSearchQueue(self.width)

        evaluator = Evaluator()
        iniAch = evaluator.evaluate(inistate)[0]
        queue.push(inistate, iniAch)
        iterationCount = 0
        printThreshold = 0
        while queue.length() > 0:
            iterationCount +=1
            if iterationCount > printThreshold:
                print("iteration Cout: " + str(iterationCount))
                printThreshold += 10
            current = queue.pop()


            for i in range(0, len(self.cameras)):
                nextState = current.move_camera(i)

                if nextState != 0:
                    result = evaluator.evaluate(nextState)
                    if result[0] == 0:
                        return result
                    if result[0] < self.best_achievement:
                        self.best_achievement = result[0]
                        self.best_setup = result[1]
                        print("new best: ", str(self.best_achievement))
                        print("setup: ", str(','.join((str(x) for x in self.best_setup))))
                    queue.push(nextState, result[0])
                    # print("Child:" + str(' '.join(str(camera) for camera in nextState.cameras)))
                if nextState == 0:
                    # print(len(stack))
                    pass
        print('bfs complete!')
        return [self.best_achievement, self.best_setup]


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
    BeamSearchTest()

def complex_setup():
    map = Map([15,15])
    map.set_cell([1, 9], [1, False])
    map.set_cell([12, 4], [0, True])
    map.set_cell([4, 6], [1, False])
    map.set_cell([5, 3], [1, False])
    map.set_cell([12, 14], [1, False])

    cameras = [Camera([0, 0], 0), Camera([0, 0], 0), Camera([0, 0], 0), Camera([0, 0], 0)]
    return (map,cameras)

def BeamSearchTest():
    # map = Map([9, 9])
    # map.set_cell([1, 7], [1, False])
    # map.set_cell([4, 4], [0, True])
    # map.set_cell([4, 6], [1, False])
    # map.set_cell([2, 3], [1, False])
    # map.set_cell([8, 8], [1, False])
    # cameras = [Camera([0, 0], 0), Camera([0, 0], 0), Camera([0, 0], 0), Camera([0, 0], 0)]
    setup = complex_setup()
    bfs = BeamSearch(setup[0], setup[1], 10)
    result = bfs.start_bfs()
    print("Final Result: ", result[0])
    print(*result[1])


if __name__ == '__main__':
    start = time.time()
    main()
    end = time.time()
    print(str((end - start)/60 ) + " min")