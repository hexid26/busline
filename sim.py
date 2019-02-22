#!/usr/bin/env python
# coding:utf-8
"""
sim.py
模拟器主程序
"""

import argparse
import logging
from include.BusRoute import BusRoute
from include.BusSimulator import BusSimulator

# path = [[300, "v5", "v2"], [200, "v5", "v2", "v1", "v4"],
#         [500, "v5", "v3", "v1"], [100, "v5", "v3"], [400, "v2", "v3", "v4"],
#         [200, "v2", "v1"], [100, "v2", "v1", "v4"], [100, "v3", "v1", "v4"],
#         [200, "v1", "v4"]]


def set_argparse():
  """Set the args&argv for command line mode"""
  parser = argparse.ArgumentParser()
  parser.add_argument("file", type=str, default="", help="input schedule file")
  parser.add_argument("--duration", "-d", type=int, default=60, help="input schedule file")
  return parser.parse_args()


def get_logger(logname):
  """Config the logger in the module
  Arguments:
      logname {str} -- logger name
  Returns:
      logging.Logger -- the logger object
  """
  logger = logging.getLogger(logname)
  formater = logging.Formatter(
      fmt='%(asctime)s - %(filename)s : %(levelname)-5s :: %(message)s',
      # filename='./log.log',
      # filemode='a',
      datefmt='%m/%d/%Y %H:%M:%S')
  stream_hdlr = logging.StreamHandler()
  stream_hdlr.setFormatter(formater)
  logger.addHandler(stream_hdlr)
  logger.setLevel(logging.DEBUG)
  return logger


__logger__ = get_logger('sim')


def main():
  """Main function"""
  __logger__.info('Process start!')
  __logger__.debug("Duration = " + str(ARGS.duration))
  bus_route = BusRoute(ARGS.file)
  sim = BusSimulator(bus_route, ARGS.duration)
  sim.add_random_passengers(2000)
  print(len(sim.passengers_list))
  # sim.save_passengers_paths("text.txt")
  sim.make_passengers_ready()
  for station in sim.stations_list:
    print(len(station.in_passenger_list))
  sim.stations_list[9].service_deploy = 1
  sim.stations_list[2].service_deploy = 1
  for time in range(0, 61):
    sim.update_on_minite(time)
  print("Data recv: %d" % sim.update_data_volume)
  # for index, passenger in enumerate(sim.passengers_list):
  #   print(
  #       str(passenger.passenger_id) + ": " + str(passenger.start_station) +
  #       str(passenger.decision_path_init))
  #   print(str(passenger.passenger_id) + ": " + str(passenger.paths))
  #   print(str(passenger.passenger_id) + ": " + str(passenger.pass_path))
  #   print('\n')
  count = 0
  for station in sim.stations_list:
    print("Station %s in: %s" % (station.station_name, station.in_passenger_list))
    print("Station %s out: %d" % (station.station_name, len(station.out_passenger_list)))
    count = count + len(station.in_passenger_list) + len(station.out_passenger_list)
  print(count)


if __name__ == '__main__':
  # Uncomment the next line to read args from cmd-line
  ARGS = set_argparse()
  main()
