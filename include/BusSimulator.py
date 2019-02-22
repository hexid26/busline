#!/usr/bin/env python
# coding:utf-8
"""BusSimulator"""
# import math
import random
import operator
import pickle
import multiprocessing
import networkx as nx
from .Bus import Bus
from .Passenger import Passenger
from .Station import Station


class BusSimulator(object):
  """公交路线的模拟器
  通过添加公交路线、车站、乘客模拟公交系统的运行状态，统计乘客上车、下车的动作
  Arguments:
      object {[type]} -- [description]
  Returns:
      [type] -- [description]
  """

  bus_route = None  # BusRoute
  duration = 0  # 服务工作的时间周期
  buses_list = []  # Bus 列表
  passengers_list = []  # 乘客列表
  stations_list = []  # 车站列表
  graph = None  # schedule 构成的图
  cores = multiprocessing.cpu_count()
  pool = multiprocessing.Pool(processes=cores)
  update_data_volume = 0

  def add_stations(self):
    """添加车站列表
    车站来源于 self.bus_route.BUS_STATIONS
    """
    self.stations_list = []
    for s_name in self.bus_route.BUS_STATIONS:
      station = Station(s_name)
      self.stations_list.append(station)
    print("Sum of bus stations : %d" % len(self.stations_list))

  def add_buses(self):
    """根据 schedule 添加对应的 bus
    schedule 来源于 self.bus_route
    """
    line_index = 0
    for line_index in range(0, len(self.bus_route.BUS_NAMES)):
      bus_index = 0
      interval_step = self.duration // self.bus_route.BUS_INTERVAL[line_index] + 1
      # print("Interval step = %d" % interval_step)
      for bus_index in range(0, interval_step):
        bus = Bus(self.bus_route.BUS_NAMES[line_index], self.bus_route.BUS_SCHEDULES[line_index],
                  bus_index * self.bus_route.BUS_INTERVAL[line_index], bus_index)
        self.buses_list.append(bus)
      line_index += 1
    print("Sum of buses added : %d" % len(self.buses_list))

  def add_random_passengers(self, p_sum):
    """随机添加若干乘客，并生成乘客的乘车方案
    Arguments:
        p_sum {int} -- 生成乘客的数量
    """
    processes = []
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    for i in range(p_sum):
      proc = multiprocessing.Process(target=self.build_random_path, args=(i, return_dict))
      processes.append(proc)
      proc.start()
    for process_item in processes:
      process_item.join()
    for index, paths in enumerate(return_dict.values()):
      passenger = Passenger(index, paths[0][0], paths[0][-1])
      passenger.paths = paths
      self.passengers_list.append(passenger)
      for cur_station in self.stations_list:
        if passenger.start_station == cur_station.station_name:
          cur_station.add_in_passenger(passenger.passenger_id)
          break
      # print("Add passenger %d." % index)
    # for cur_station in self.stations_list:
    #   print(cur_station.in_passenger_list)

  def build_random_path(self, p_index, return_dict):
    """随机生成路径
    Arguments:
        p_index {int} -- 路径编号
        return_dict {dict} -- 保存乘车方案的词典
    """
    flag_found_path = False
    while not flag_found_path:
      viable_paths = []
      found_path = []
      start_station = random.sample(self.stations_list, 1)[0].station_name
      end_station = random.sample(self.stations_list, 1)[0].station_name
      # print("Passenger %d :: Start from %s, end at %s" %
      #       (p_index, start_station, end_station))
      if start_station == end_station:
        continue
      feasible_paths = nx.algorithms.simple_paths.all_simple_paths(self.graph, start_station,
                                                                   end_station)
      if feasible_paths == []:
        continue
      feasible_paths = sorted(feasible_paths, key=lambda x: len(x))
      for index_path, path in enumerate(feasible_paths):
        if index_path >= 2:
          break
        # print(path)
        found_path = self.find_all_paths(path)
        if found_path != []:
          viable_paths += found_path
          flag_found_path = True
      if not flag_found_path:
        continue
      # print("Passenger %d:" % p_index)
      viable_paths = self.sort_paths(viable_paths)
      # for path in viable_paths:
      #     print("可行路径 %s" % path)
    return_dict[p_index] = viable_paths

  def path_time(self, path):
    """计算乘车方案的时间开销
    Arguments:
        path {list} -- 乘车方案
    Returns:
        int -- 乘车方案对应的耗时
    """
    time = 0
    for index in range(2, len(path), 3):
      time += path[index]
    return time

  def sort_paths(self, viable_paths):
    """对乘车方案进行排序
    Arguments:
        viable_paths {list} -- 乘车方案的列表
    Returns:
        list -- 排序后的乘车方案列表
    """
    # ! 优先最快方案
    sorted_paths = sorted(viable_paths, key=lambda x: len(x))
    sorted_paths = sorted(sorted_paths, key=self.path_time)
    # ! 优先直达方案
    # sorted_paths = sorted(viable_paths, key=self.path_time)
    # sorted_paths = sorted(sorted_paths, key=lambda x: len(x))
    for path in sorted_paths:
      for cnt in range(1, (len(path) // 3) + 1):
        del path[2 * cnt]
    return sorted_paths

  def find_direct_paths(self, path):
    """找出乘客站到站路径的直达车
    Arguments:
        path {list} -- 乘客的站到站路径
    Returns:
        list -- 直达车方案
    """
    direct_paths = []
    path_time = 0
    for schedule_path in self.bus_route.BUS_SCHEDULES:
      # print("%s in %s" % (path, schedule_path[0]))
      if any([
          path == schedule_path[0][i:i + len(path)]
          for i in range(0,
                         len(schedule_path[0]) - len(path) + 1)
      ]):
        start_index = schedule_path[0].index(path[0])
        end_index = schedule_path[0].index(path[-1])
        path_time = (schedule_path[1][end_index] - schedule_path[1][start_index])
        bus_index = self.bus_route.BUS_SCHEDULES.index(schedule_path)
        direct_paths.append([self.bus_route.BUS_NAMES[bus_index], path_time, path[-1]])
    if direct_paths != []:
      direct_paths.sort(key=operator.itemgetter(0))
    return direct_paths

  def find_all_paths(self, path):
    """找出左右的乘车方案
    Arguments:
        path {list} -- 乘客的站到站路径
    Returns:
        list -- 走输入路径的乘车方案
    """
    # print(path)
    all_paths = []
    tmp_paths = self.find_direct_paths(path)
    all_paths += tmp_paths
    if all_paths == []:
      tmp_paths = []
      for step_i in range(2, len(path)):
        tmp_paths_step_1 = self.find_direct_paths(path[0:step_i])
        tmp_paths_step_2 = self.find_direct_paths(path[step_i - 1:len(path)])
        if tmp_paths_step_1 != [] and tmp_paths_step_2 != []:
          for d_path_1 in tmp_paths_step_1:
            for d_path_2 in tmp_paths_step_2:
              tmp_paths.append(d_path_1 + d_path_2)
      all_paths += tmp_paths
      if all_paths == []:
        tmp_paths = []
        for step_i in range(2, len(path) - 1):
          for step_j in range(step_i + 1, len(path)):
            tmp_paths_step_1 = self.find_direct_paths(path[0:step_i])
            tmp_paths_step_2 = self.find_direct_paths(path[step_i - 1:step_j])
            tmp_paths_step_3 = self.find_direct_paths(path[step_j - 1:len(path)])
            if tmp_paths_step_1 != [] and tmp_paths_step_2 != [] and tmp_paths_step_3 != []:
              for d_path_1 in tmp_paths_step_1:
                for d_path_2 in tmp_paths_step_2:
                  for d_path_3 in tmp_paths_step_3:
                    tmp_paths.append(d_path_1 + d_path_2 + d_path_3)
        all_paths += tmp_paths
    for d_path in all_paths:
      d_path.insert(0, path[0])
    return all_paths

  def print_buses(self):
    """打印采集时间段内所有的公交车站信息
    """
    for bus in self.buses_list:
      print("==========\nBusName = %s, BusID = %d, StartTime = %d\nStations = %s\nSchedule = %s\n" %
            (bus.bus_name, bus.bus_index, bus.start_time, bus.bus_stations, bus.bus_schedule))

  def build_graph(self):
    """根据公交车的规划建立站点之间的有向图(NetworkX)
    """
    self.graph = nx.DiGraph()
    self.graph.add_edges_from(self.bus_route.NETWORK_EDGES)
    # print(self.graph.nodes())
    # print(self.graph.edges())

  def save_passengers_paths(self, outfile):
    """保存所有乘客的可行路径
    Arguments:
        outfile {str} -- 存储的文件名
    """
    all_paths = []
    for passenger in self.passengers_list:
      all_paths.append(passenger.paths)
    with open(outfile, 'wb') as fp:
      # for passenger in self.passengers_list:
      # fp.write((str)(passenger.paths) + '\n')
      pickle.dump(all_paths, fp)

  def update_on_minite(self, time):
    # print("----- Bus Update at time %d -----" % time)
    for cur_bus in self.buses_list:
      cur_station_name = cur_bus.get_status(time)
      if cur_station_name == '':
        continue
      else:
        # print("Bus %s, ID %d, is at station %s" % (cur_bus.bus_name, cur_bus.bus_index,
        #                                            cur_station_name))
        for cur_station in self.stations_list:
          if cur_station.service_deploy == 1:
            for passenger_id_upload in cur_station.in_passenger_list:
              if self.passengers_list[passenger_id_upload].upload_data():
                self.update_data_volume += 1
          if cur_station.station_name == cur_station_name:
            # for passenger_id in cur_bus.passengers_list:
            # self.passengers_list[passenger_id].pass_path.append(cur_station_name)
            # print(cur_station.station_name)
            # cur_station.add_stoped_bus(cur_bus)
            # if cur_bus.bus_name == 'No1' and cur_bus.bus_index == 0:
            #   print("bus 0 is at station %s" % cur_station_name)
            # ! 下车
            delete_id = []
            for passenger_id_down in cur_bus.passengers_list:
              self.passengers_list[passenger_id_down].pass_path.append(cur_station_name)
              if cur_station.service_deploy == 1:
                if self.passengers_list[passenger_id_down].upload_data():
                  self.update_data_volume += 1
              if self.passengers_list[passenger_id_down].decision_path[
                  0] == cur_station.station_name:
                # print(self.passengers_list[passenger_id_down].decision_path[0],
                #       cur_station.station_name)
                # print("take off the bus %d" % passenger_id_down)
                delete_id.append(passenger_id_down)
                if len(self.passengers_list[passenger_id_down].decision_path) == 1:
                  # * 到终点站
                  cur_station.add_out_passenger(passenger_id_down)
                else:
                  # * 到中转站
                  cur_station.add_in_passenger(passenger_id_down)
                  self.passengers_list[passenger_id_down].decision_path = self.passengers_list[
                      passenger_id_down].decision_path[1:]
            # print("To delete: %s" % delete_id)
            for delete_passenger_id in delete_id:
              # print("Delete %d from %s" % (delete_passenger_id, cur_bus.passengers_list))
              cur_bus.passengers_list.remove(delete_passenger_id)
    for cur_bus in self.buses_list:
      cur_station_name = cur_bus.get_status(time)
      if cur_station_name == '':
        continue
      else:
        # print("Bus %s, ID %d, is at station %s" % (cur_bus.bus_name, cur_bus.bus_index,
        #                                            cur_station_name))
        for cur_station in self.stations_list:
          if cur_station.service_deploy == 1:
            for passenger_id_upload in cur_station.in_passenger_list:
              if self.passengers_list[passenger_id_upload].upload_data():
                self.update_data_volume += 1
          if cur_station_name == cur_station.station_name:
            # print("BUS %s ID %d with passengers %s, at station %s, passengers sum %d : %s" %
            #       (cur_bus.bus_name, cur_bus.bus_index,
            #        cur_bus.passengers_list, cur_station.station_name,
            #        len(cur_station.in_passenger_list), str(cur_station.in_passenger_list)))
            delete_id = []
            for passenger_id_up in cur_station.in_passenger_list:
              # ! 上车
              # print("process passenger:%d" % passenger_id_up)
              if cur_bus.is_full():
                # print("Time %d, Bus %s ID %d is full" % (time, cur_bus.bus_name, cur_bus.bus_index))
                # print(cur_bus.passengers_list)
                break
              if self.passengers_list[passenger_id_up].decision_path == []:
                # * 第一次上车
                for path in self.passengers_list[passenger_id_up].paths:
                  if path[0] == cur_bus.bus_name:
                    # print("%s = %s" % (path[0], cur_bus.bus_name))
                    if cur_bus.add_passenger(passenger_id_up):
                      # print("Bus %s ID %d with passengers %s" %
                      #       (cur_bus.bus_name, cur_bus.bus_index, cur_bus.passengers_list))
                      delete_id.append(passenger_id_up)
                      self.passengers_list[passenger_id_up].decision_path = path[1:]
                      self.passengers_list[passenger_id_up].decision_path_init = path
                      self.passengers_list[passenger_id_up].pass_path.append(
                          cur_station.station_name)
                      break
              else:
                # * 上过车
                if self.passengers_list[passenger_id_up].decision_path[0] == cur_bus.bus_name:
                  if cur_bus.add_passenger(passenger_id_up):
                    delete_id.append(passenger_id_up)
                    self.passengers_list[passenger_id_up].decision_path = self.passengers_list[
                        passenger_id_up].decision_path[1:]
                    continue
            for delete_passenger_id in delete_id:
              cur_station.in_passenger_list.remove(delete_passenger_id)
            break
          else:
            continue
      # if time == 0:
      #   print("Bus %s, ID %d, at %s: %s" % (cur_bus.bus_name, cur_bus.bus_index,
      #                                       cur_bus.bus_stations[0], cur_bus.passengers_list))

  def make_passengers_ready(self):
    for passenger in self.passengers_list:
      for path_index in range(0, len(passenger.paths)):
        passenger.paths[path_index] = passenger.paths[path_index][1:]

  def __init__(self, bus_route_in, duration_in):
    self.update_data_volume = 0
    self.buses_list = []
    self.passengers_list = []
    self.stations_list = []
    self.graph = None
    self.cores = multiprocessing.cpu_count()
    self.pool = multiprocessing.Pool(processes=self.cores)
    self.bus_route = bus_route_in
    self.duration = duration_in
    self.build_graph()
    self.add_buses()
    self.add_stations()
    # print(self.bus_route.BUS_SCHEDULES)
