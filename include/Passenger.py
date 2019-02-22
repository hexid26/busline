#!/usr/bin/env python
# coding:utf-8
"""Passenger"""


class Passenger(object):
  passenger_id = 0
  start_station = ''
  end_station = ''
  sensing_data_exsited = 1
  decision_path = []
  decision_path_init = []
  paths = []  # (站点，时间)
  pass_path = []

  def upload_data(self):
    """上传数据

        如果经过的车站具备服务，则上传数据
        Returns:
            [bool] -- True 表示上传；False 表示不上传
        """
    if self.sensing_data_exsited == 1:
      self.sensing_data_exsited = 0
      return True
    else:
      return False

  def __init__(self, id_in, start_station_in, end_station_in):
    """乘客的构造函数

        Arguments:
            id_in {int} -- 乘客 id
            start_station_in {str} -- 乘客的起始站
            end_station_in {str} -- 乘客的到达站
        """
    self.passenger_id = id_in
    self.start_station = start_station_in
    self.end_station = end_station_in
    self.sensing_data_exsited = 1
    self.decision_path = []
    self.paths = []
    self.decision_path_init = []
    self.pass_path = []
