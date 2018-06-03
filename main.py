import copy
# import numpy as np
import time
import random


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

    def set_dir(self, dir):
        self.orientation = dir

    def __str__(self):
        return "[{}, {}]".format(self.position, self.orientation)

class State:
    def __init__(self, map, cameras):
        self.map = map
        self.cameras = cameras
        self.ach = 1000
    def update_cams(self, add, delete):
        for z in range(len(self.cameras)):
            if self.cameras[z] == delete:
                self.cameras[z] = add
                return True
        return False
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


    #computed achievement for 1 camera orientation setup
    def compute_achievement(self, cameras, map):
        local_map = copy.deepcopy(map)
        achievement = 0
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

        if camera.orientation == 2:
            while temp_position[0] + 1 <= len(map.grid) -1:
                if map.grid[temp_position[0]+1][temp_position[1]][1] :
                    return
                map.grid[temp_position[0]+1][temp_position[1]][0] -=1
                temp_position[0] += 1

        if camera.orientation == 3:
            while temp_position[1] + 1  <= len(map.grid[0]) -1:
                if map.grid[temp_position[0]][temp_position[1] +1][1]:
                    return
                map.grid[temp_position[0]][temp_position[1] +1][0] -=1
                temp_position[1] += 1
        # print(camera, map)

#Beam Search
class BeamSearch:
    def __init__(self, map, cameras, beam_width):
        self.best_achievement = map.total_priority
        self.best_setup = cameras
        self.cameras = cameras
        self.map = map
        self.width = beam_width

class TabuSearch:
    def __init__(self, map, cameras):
        self.map = map
        self.cams = cameras
        self.CandiList = CandiList(cameras, map)
        map_size = map.dimention[0]
        self.ListTTL = ListTTL(map_size)
        self.improve_limit = 10000
        self.iteration_limit = 1000

    def start_tabu(self):
        cur_state = State(self.map, self.cams)
        eva = Evaluator()
        cur_state.ach = eva.compute_achievement(self.cams, self.map)
        best_state = cur_state
        best_state.ach = 1000
        impro_count = 0
        iterat_count = 0

        #compute candidate list
        while(1):
            self.CandiList.comp_list(cur_state.ach)
            print("cur ach value: ", cur_state.ach)
            iterat_count += 1
            element_index = 0
            for candi in self.CandiList.List:
                element_index += 1
                #check if the candi is tabuted
                if self.ListTTL.check_tabuted(candi.add, candi.delete):
                    a = "a"
                elif candi.del_ach <1000:
                    #update current state to the candi
                    cur_state.ach += candi.del_ach
                    result = cur_state.update_cams(candi.add, candi.delete)
                    print(result)
                    print("cam added: ", candi.add)
                    print("cam delete: ", candi.delete)
                    #update cur_cams in CandiList
                    self.CandiList.cur_cams = cur_state.cameras
                    #update best state
                    print("cur_state.ach: ", cur_state.ach)
                    #print cams
                    for cam in cur_state.cameras:
                        print(cam)
                    if cur_state.ach < best_state.ach:
                        best_state = cur_state
                        impro_count = 0
                        print(impro_count)
                    else:
                        impro_count += 1
                        print(impro_count)
                    #end if improve_limit iterations from last improvement
                    if impro_count > self.improve_limit:
                        print ("reach improve limit")
                        print("iteration: ", iterat_count)
                        print("ach: ", best_state.ach)
                        print(best_state.map, best_state.cameras)
                        return
                    #update TTL list
                    self.ListTTL.update_TTL_List(candi.add, candi.delete)
                    break;
                elif element_index == len(self.CandiList.List) - 1:
                    #reached the end of candidate list, and all records are tabuted or out of bound
                    print ("no suitable option found in candidate list")
                    print("iteration: ", iterat_count)
                    print(best_state.map, best_state.cameras)
                    print("ach: ", best_state.ach)
                    return
            #end if ach value = 0
            if cur_state.ach == 0:
                print ("found the optima")
                print("iteration: ", iterat_count)
                print("ach: ", cur_state.ach)
                print(cur_state.map, cur_state.cameras)
                return
            # end if exceeded iteration limit
            if iterat_count > self.iteration_limit:
                print ("exceeded iteration limit")
                print("iteration: ", iterat_count)
                print("ach: ",best_state.ach )
                print(best_state.map, best_state.cameras)
                return


class CandiList:
    def __init__(self, cur_cams, map):
        self.List = [Candi() for i in range(16*len(cur_cams))]
        self.map = map
        self.cur_cams = cur_cams

    def comp_list(self, cur_ach):
        this_cam = Camera([0, 0], 0)
        temp_cams = copy.deepcopy(self.cur_cams)
        temp_ach = 0
        for num_cam in range(0, len(self.cur_cams)):
            for j in range(1,17):
                this_cam = Camera([0, 0], 0)
                if 1 <= j <= 4:
                    this_cam = Camera([self.cur_cams[num_cam].position[0] - 1, self.cur_cams[num_cam].position[1]])
                if 5 <= j <= 8:
                    this_cam = Camera([self.cur_cams[num_cam].position[0], self.cur_cams[num_cam].position[1] + 1])
                if 9 <= j <= 12:
                    this_cam = Camera([self.cur_cams[num_cam].position[0] + 1, self.cur_cams[num_cam].position[1]])
                if 13 <= j <= 16:
                    this_cam = Camera([self.cur_cams[num_cam].position[0], self.cur_cams[num_cam].position[1] - 1])
                this_cam.set_dir((j-1)%4)

                # print("j: ", j,"cur cam pos 0:",self.cur_cams[num_cam].position[0], this_cam)

                self.List[(num_cam-1)*16 + j -1].add = this_cam
                self.List[(num_cam - 1) * 16 + j -1].delete = self.cur_cams[num_cam]

                temp_cams[num_cam] = this_cam

                #check cell within the map
                if 0 <= this_cam.position[0] < self.map.dimention[0] and 0 <= this_cam.position[1] < self.map.dimention[1]:
                    temp_ach = Evaluator().compute_achievement(temp_cams, self.map)
                    self.List[(num_cam - 1) * 16 + j -1].del_ach = temp_ach - cur_ach
                else:
                    self.List[(num_cam - 1) * 16 + j - 1].del_ach = -1000

        #sort list by delta ach
        # self.List.sort(key=lambda x: x.add.position[1], reverse=True)
        # self.List.sort(key=lambda x: x.delete.position[1], reverse=False)
        random.shuffle(self.List)
        self.List.sort(key=lambda x : x.del_ach, reverse = False)
        for l in self.List:
            print("add: ", l.add, "    delete: ", l.delete, "   delta ach: ", l.del_ach)
class Candi:
    def __init__(self):
        self.del_ach = 1000
        self.add = Camera([0,0],0)
        self.delete = Camera([0, 0], 0)

class ListTTL:
    def __init__(self, size):
        cam = Camera([0,0],0)
        cam1 = Camera([0,0],0)
        record_ttl = RecordTTL(cam,cam1,0)
        self.List = [copy.deepcopy(record_ttl) for j in range(size)]
        self.size = size
        for a in self.List:
            a.cam1 = Camera([0,0],0)
            a.cam2 = Camera([0, 0], 0)
            a.TTL = 0

    #check if cam1 position and cam2 position can be switch places
    def check_tabuted(self, cam1, cam2):
        for e in self.List:
            if e.cam1.position == cam1.position and e.cam2.position == cam2.position:
                return True
            elif e.cam2.position == cam1.position and e.cam1.position == cam2.position:
                return True
        return False

    #decrease TTL by 1 for all record, add newly tabuted record
    def update_TTL_List(self, cam1, cam2):
        flag = True
        for record_ttl in self.List:
            if record_ttl.TTL == 0 and flag:
                flag = False
                record_ttl.cam1 = cam1
                record_ttl.cam2 = cam2
                record_ttl.TTL = self.size
            elif record_ttl.TTL > 0:
                record_ttl.TTL -= 1
        # #print tabu list
        # for t in self.List:
        #     print("cam1: ", t.cam1, "cam2: ", t.cam2, "TTL:", t.TTL)


class RecordTTL:
    def __init__(self, cam1, cam2, TTL):
        self.cam1 = cam1
        self.cam2 = cam2
        self.TTL = TTL

def main():
    #initialize map
    tabu_search()

def complex_setup():
    map = Map([15,15])
    map.set_cell([1, 9], [1, False])
    map.set_cell([12, 4], [0, True])
    map.set_cell([4, 6], [1, False])
    map.set_cell([5, 3], [1, False])
    # map.set_cell([6, 7], [1, False])
    # map.set_cell([10, 14], [1, False])
    # map.set_cell([11, 2], [1, False])
    # map.set_cell([12, 6], [1, False])
    # map.set_cell([13, 10], [1, False])
    # map.set_cell([14, 5], [1, False])

    cameras = [Camera([0, 0], 0), Camera([0, 0], 0), Camera([0, 0], 0)]
    return (map,cameras)

def BeamSearchTest():
    # map = Map([9, 9])
    #map.set_cell([1, 7], [1, False])
    # map.set_cell([4, 4], [0, True])
    # map.set_cell([4, 6], [1, False])
    # map.set_cell([2, 3], [1, False])
    # map.set_cell([8, 8], [1, False])
    # cameras = [Camera([0, 0], 0), Camera([0, 0], 0), Camera([0, 0], 0), Camera([0, 0], 0)]
    setup = complex_setup()
    bfs = BeamSearch(setup[0], setup[1], 10)
    result = bfs.start_bfs()
    print("Final Result: ", result[0])

def tabu_search():
    map = Map([4, 4])
    map.set_cell([1,1],[1,False])
    map.set_cell([2, 2], [1, False])
    map.set_cell([1, 2], [1, False])
    map.set_cell([2, 1], [1, False])
    # setup = complex_setup()
    cameras = [Camera([0, 0], 0), Camera([3, 3], 0),Camera([3, 3], 0),Camera([3, 3], 0)]
    tabu = TabuSearch(map, cameras)
    tabu.start_tabu()



if __name__ == '__main__':
    start = time.time()
    main()
    end = time.time()
    print(str((end - start)/60 ) + " min")