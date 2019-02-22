#!/usr/bin/env python
# coding:utf-8
"""Station"""


class Station(object):
  station_name = ''
  in_passenger_list = []  # [passenger_list]
  stoped_buses_list = []  # (bus_name, time)
  out_passenger_list = []  # [passenger_list]
  service_deploy = 0
  get_data_passenger_list = []

  def add_in_passenger(self, passenger_id):
    """乘客进站

        Arguments:
            passenger {Passenger} -- 进站的乘客对象
        """
    self.in_passenger_list.append(passenger_id)

  def add_out_passenger(self, passenger_id):
    """乘客出站

        Arguments:
            passenger {Passenger} -- 出站的乘客对象
        """
    self.out_passenger_list.append(passenger_id)

  def add_stoped_bus(self, bus):
    """添加停靠的 bus

        Arguments:
            bus {Bus} -- 出站的bus对象
        """
    self.stoped_buses_list.append(bus.bus_name)

  def __init__(self, name_in):
    """车站的构造函数

        Arguments:
            name_in {str} -- 车站名
        """
    self.station_name = name_in
    self.in_passenger_list = []
    self.stoped_buses_list = []
    self.out_passenger_list = []
    self.service_deploy = 0
    self.get_data_passenger_list = []
