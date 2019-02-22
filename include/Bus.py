#!/usr/bin/env python
# coding:utf-8
"""Bus"""


class Bus(object):
  bus_name = ''
  bus_index = 0
  start_time = 0
  duration = 0
  bus_stations = []  # station at time
  bus_schedule = []  # time
  passengers_list = []

  def get_status(self, time_point):
    if time_point in self.bus_schedule:
      index = self.bus_schedule.index(time_point)
      return self.bus_stations[index]
    else:
      return ''

  def is_full(self):
    if len(self.passengers_list) >= 50:
      return True
    else:
      return False

  def add_passenger(self, passenger_id):
    if len(self.passengers_list) >= 50:
      return False
    else:
      self.passengers_list.append(passenger_id)
      return True

  def __init__(self, name_in, bus_schedule_in, start_time_in, bus_index_in):
    self.bus_name = name_in
    self.bus_index = bus_index_in
    self.bus_stations = bus_schedule_in[0]
    # self.bus_schedule = bus_schedule_in[1]
    self.start_time = start_time_in
    self.bus_schedule = [x + start_time_in for x in bus_schedule_in[1]]
    self.duration = self.bus_schedule[-1]
    self.passengers_list = []
