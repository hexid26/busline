#!/usr/bin/env python
# coding:utf-8
"""test_stations.py"""

# import argparse

import logging


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


__logger__ = get_logger('test_stations')


def random_generate_buslist(bus_sum, station_sum):
    """build a buslist randomly
    
    Returns:
        [list] -- list built randomly
    """
    buslist = []
    for bus_id in range(1, bus_sum + 1):
        pass
    return buslist


def save_schedule(buslist, bus_interval, filename):
    """Save schedule to Schedule folder

    Arguments:
        buslist {list} -- list of busline
        filename {str} -- filename used for save
    """
    with open('Schedule/' + 'test_busline.txt', 'w') as fp:
        index = 1
        fp.write("# [BusName],[Interval]:[StartStation],[StopStation],[TimePoint];\n")
        for busline in buslist:
            fp.write("%s,%d:" % (index, bus_interval[index-1]))
            fp.write(';'.join("%s,%s" % item for item in busline))
            fp.write('\n')
            index += 1


def main():
    """Main function"""
    __logger__.info('Process start!')
    buslist = []
    bus_interval = []
    buslist.append([("S1", 0), ("S2", 2), ("S3", 5), ("S6", 7)])
    bus_interval.append(8)
    buslist.append([("S2", 0), ("S5", 2), ("S4", 4), ("S7", 8)])
    bus_interval.append(10)
    buslist.append([("S7", 0), ("S8", 2), ("S5", 4), ("S6", 8), ("S10", 11)])
    bus_interval.append(8)
    buslist.append([("S3", 0), ("S5", 2), ("S9", 4), ("S10", 7)])
    bus_interval.append(9)
    buslist.append([("S8", 0), ("S7", 2), ("S4", 4), ("S5", 7), ("S6", 9),
                    ("S3", 12)])
    bus_interval.append(10)
    save_schedule(buslist, bus_interval, 'test_busline.txt')
    # TODO: process lines...
    __logger__.info('Process end!')


if __name__ == '__main__':
    # Uncomment the next line to read args from cmd-line
    # ARGS = set_argparse()
    main()