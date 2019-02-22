#!/usr/bin/env python
# coding:utf-8
"""sim.py"""

# TODO 根据 schedule 把自动生成 Paths，Paths 的结果要可以并入到 gurabi 的程序当中。

import argparse
import logging
# import networkx as nx
# import matplotlib.pyplot as plt
from include.BusRoute import BusRoute
from include.Passenger import Passenger
from include.BusSimulator import BusSimulator

path = [[300, "v5", "v2"], [200, "v5", "v2", "v1", "v4"],
        [500, "v5", "v3", "v1"], [100, "v5", "v3"], [400, "v2", "v3", "v4"],
        [200, "v2", "v1"], [100, "v2", "v1", "v4"], [100, "v3", "v1", "v4"],
        [200, "v1", "v4"]]


def set_argparse():
  """Set the args&argv for command line mode"""
  parser = argparse.ArgumentParser()
  parser.add_argument(
      "file", type=str, default="", help="input schedule file")
  parser.add_argument(
      "outfile", type=str, default="", help="output path file")
  parser.add_argument(
      "--duration", "-d", type=int, default=60, help="input schedule file")
  return parser.parse_args()


def get_logger(logname: str):
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
  __logger__.debug("Duration = %d" % ARGS.duration)
  bus_route = BusRoute(ARGS.file)
  sim = BusSimulator(bus_route, ARGS.duration)
  sim.add_random_passengers(500)
  print(len(sim.passengers_list))
  sim.save_passengers_paths(ARGS.outfile)


if __name__ == '__main__':
  # Uncomment the next line to read args from cmd-line
  ARGS = set_argparse()
  main()
