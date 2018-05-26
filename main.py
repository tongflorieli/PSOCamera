import copy
class Cell:
    "Basic cell"
    cellCount = 0
    def __init__(self, priority, wall):
        self.priority = priority
        self.up, self.right, self.down, self.left = wall[0], wall[1], wall[2], wall[3]
        self.id = Cell.cellCount
        Cell.cellCount += 1

class Map:
    "Map"
    def __init__(self, dimention):
        self.dimention = dimention
        self.cells = [[Cell(0,[0,0,0,0]) for i in range(dimention[0])] for j in range(dimention[1])]
        self.totalPriority = 0

    def set_cell(self, position, cell):
        self.cells[position[0]][position[1]] = cell
        if cell.priority ==1 :
            self.totalPriority += 1


class Camera:
    def __init__(self, position):
        "0 = left, 1 = up, 2 = right, 3 = down"
        self.position = position
        self.orientation = 0


class State:
    "state, cameras has to be array"
    def __init__(self, map, cameras):
        self.map = map
        self.cameras = cameras
        self.minAchievement = map.totalPriority
        self.bestSetup = copy.deepcopy(cameras)
        self.__compute_min_achievement(cameras)

    def move_camera(self, camera_num):
        position = self.cameras[camera_num].position
        dimention = self.map.dimention
        if position[0] >= dimention[0] - 1:
            position[0] = 0
            position[1] += 1
        elif position[0] >= dimention[0] - 1 and position[1] >= dimention[1] - 1:
            #reached the end
            return 0
        else:
            position[0] += 1
            return State(self.map, copy.deepcopy(self.cameras))


    def __compute_Achievement(self):
        ss_map = copy.deepcopy(self.map)

        for camera in self.cameras:
            self.__set_visible(camera, ss_map)
        achivement = 0
        for i in ss_map.cells:
            for j in i:
                if j.priority > 0:
                    achivement += j.priority
        return achivement

    def __compute_min_achievement(self, camera):
        if len(camera) == 1:
            achievement = self.__compute_Achievement()
            if achievement < self.minAchievement:
                self.minAchievement = achievement
                self.bestSetup = copy.deepcopy(self.cameras)
        else:
            while camera[0].orientation <= 3:
                new_camera = copy.deepcopy(camera)
                self.__compute_min_achievement(new_camera[1:])
                camera[0].orientation += 1

    def __set_visible(self, camera, map):
        map.cells[camera.position[0] - 1][camera.position[1] ].priority -= 1
        map.cells[camera.position[0] + 1][camera.position[1] ].priority -= 1
        map.cells[camera.position[0] ][camera.position[1] + 1].priority -= 1
        map.cells[camera.position[0] ][camera.position[1] - 1].priority -= 1
    #    if camera.orientation == 0:
    #        if camera.position[0] - 1 >= 0 and camera.position[1] - 1 >= 0 and map.cells[camera.position[0]-1][camera.position[0] - 1].down == 0:
    #            map.cells[camera.position[0]-1][camera.position[1]-1].priority -= 1
    #        if camera.position[0] - 1 >= 0 and camera.position[1]  >= 0 and map.cells[camera.position[0]-1][camera.position[0]].right == 0:
    #            map.cells[camera.position[0]-1][camera.position[1]].priority -= 2
    #        if camera.position[0] - 1 >= 0 and camera.position[1] + 1 >= 0 and map.cells[camera.position[0]-1][camera.position[0] + 1].up == 0:
    #            map.cells[camera.position[0]-1][camera.position[1]+1].priority -= 1
    #    if camera.orientation == 1:
    #        if camera.position[0] - 1 >= 0 and camera.position[1] - 1 >= 0 and map.cells[camera.position[0]-1][camera.position[0] - 1].right == 0:
    #            map.cells[camera.position[0]-1][camera.position[1]-1].priority -= 1
    #        if camera.position[0]  >= 0 and camera.position[1] -1 >= 0 and map.cells[camera.position[0]][camera.position[0] - 1].down == 0:
    #            map.cells[camera.position[0]][camera.position[1] -1].priority -= 2
    #        if camera.position[0] + 1 >= 0 and camera.position[1] - 1 >= 0 and map.cells[camera.position[0]+1][camera.position[0] - 1].left == 0:
    #            map.cells[camera.position[0]+1][camera.position[1]-1].priority -= 1
    #    if camera.orientation == 1:
    #        if camera.position[0] - 1 >= 0 and camera.position[1] - 1 >= 0 and map.cells[camera.position[0]-1][camera.position[0] - 1].right == 0:
    #            map.cells[camera.position[0]-1][camera.position[1]-1].priority -= 1
    #        if camera.position[0]  >= 0 and camera.position[1] -1 >= 0 and map.cells[camera.position[0]][camera.position[0] - 1].down == 0:
    #            map.cells[camera.position[0]][camera.position[1] -1].priority -= 2
    #        if camera.position[0] + 1 >= 0 and camera.position[1] - 1 >= 0 and map.cells[camera.position[0]+1][camera.position[0] - 1].left == 0:
    #            map.cells[camera.position[0]+1][camera.position[1]-1].priority -= 1

class BFS:
    def __init__(self, map, cameras):
        self.inistate = State(map,cameras)
        self.best_achievement = self.inistate.minAchievement
        self.best_setup = self.inistate.bestSetup
        self.cameras = cameras

    def start_bfs(self):
        stack = []
        stack.insert(0, self.inistate)
        while len(stack) > 0:
            current = stack.pop()
            if current.minAchievement < self.best_achievement:
                current.minAchievement = self.best_achievement
                current.bestSetup = self.best_setup
            for index, camera in enumerate(self.cameras):
                nextState = current.move_camera(index)
                if nextState != 0:
                    stack.insert(0,nextState)
        print('bfs complete!')
        return

def main():
    print('start')
    map = Map([5,5])
    map.set_cell([1,1], Cell(1, [0,0,0,0]))
    cameras = [Camera([0,0])]*1
    #print(cameras)
    #bfs = BFS(map,cameras)

    state = State(map,cameras)
    state = state.move_camera(0)
    print('done')

    test = [1,2,3]
    print(test[-1])




main()