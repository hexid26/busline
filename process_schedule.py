#!/usr/bin/env python
# coding:utf-8
"""process_schedule.py"""

# TODO 根据 schedule 把自动生成 Paths，Paths 的结果要可以并入到 gurabi 的程序当中。

import argparse
import logging
# import networkx as nx
# import matplotlib.pyplot as plt
# from threading import Thread
from include.BusRoute import BusRoute
from include.Simulator import Simulator
from include.Passenger import Passenger

path = [[300, "v5", "v2"], [200, "v5", "v2", "v1", "v4"],
        [500, "v5", "v3", "v1"], [100, "v5", "v3"], [400, "v2", "v3", "v4"],
        [200, "v2", "v1"], [100, "v2", "v1", "v4"], [100, "v3", "v1", "v4"],
        [200, "v1", "v4"]]


def set_argparse():
    """Set the args&argv for command line mode"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "file", type=str, default="", help="input schedule file")
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


__logger__ = get_logger('process_schedule')


def main():
    """Main function"""
    __logger__.info('Process start!')
    new_lines = []
    with open(ARGS.file, 'r') as fp:
        for line in fp:
            time_point = 0
            for index in range(0, line.count('-')):
                line = line.replace("-", "," + str(time_point) + ";", 1)
                time_point += 5
            line = line.replace("\n", "," + str(time_point) , 1)
            new_lines.append(line)
    with open("new_schedule.txt", 'w') as fp:
        for line in new_lines:
            fp.write(line+"\n")
    print(len(new_lines))
    exit(0)


if __name__ == '__main__':
    # Uncomment the next line to read args from cmd-line
    ARGS = set_argparse()
    main()
