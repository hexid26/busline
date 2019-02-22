#!/usr/bin/env python
# coding:utf-8
"""BusRoute"""


class BusRoute(object):
    read_file = ''
    BUS_NAMES = []  # list of busname
    BUS_INTERVAL = []  # list of interval
    BUS_LINES = []  # list of ((station,station),time)***
    BUS_SCHEDULES = []  # list of [[stations,***],[time_point,***]]***
    BUS_LINE_STEPS = []  # list of ((station,station),time)
    BUS_STATIONS = []  # list of station
    NETWORK_EDGES = []  # list of (station,station)***

    def print_bus_lines(self):
        for bus_line in self.BUS_LINES:
            print("%s" % bus_line)

    def print_stations(self):
        print("%s" % self.BUS_STATIONS)

    def process_file(self):
        """read schedule file and build route info
        """
        with open(self.read_file, 'r') as fp:
            for line in fp:
                if line[0] == '#':
                    continue
                bus_info = line.split(':')[0]
                self.BUS_NAMES.append(bus_info.split(',')[0])
                self.BUS_INTERVAL.append(int(bus_info.split(',')[1]))
                line = line.split(':')[1]
                line = line.rstrip('\n')
                # __logger__.debug(line)
                station_items = line.split(';')
                bus_line = []
                for station_cnt in range(1, len(station_items)):
                    edge = (station_items[station_cnt - 1].split(',')[0],
                            station_items[station_cnt].split(',')[0])
                    # __logger__.debug(edge)
                    edge_timecost = (int)(
                        station_items[station_cnt].split(',')[1]) - (int)(
                            station_items[station_cnt - 1].split(',')[1])
                    # __logger__.debug(edge_timecost)
                    self.BUS_LINE_STEPS.append((edge, edge_timecost))
                    bus_line.append((edge, edge_timecost))
                self.BUS_LINES.append(bus_line)
                bus_stations = []
                bus_schedule = []
                for station_cnt in range(0, len(station_items)):
                    bus_stations.append(
                        station_items[station_cnt].split(',')[0])
                    bus_schedule.append(
                        int(station_items[station_cnt].split(',')[1]))
                self.BUS_SCHEDULES.append((bus_stations, bus_schedule))
        for item in self.BUS_LINE_STEPS:
            if item[0][0] not in self.BUS_STATIONS:
                self.BUS_STATIONS.append(item[0][0])
            if item[0][1] not in self.BUS_STATIONS:
                self.BUS_STATIONS.append(item[0][1])
            # __logger__.debug(item[0])
            if item[0] not in self.NETWORK_EDGES:
                self.NETWORK_EDGES.append(item[0])
        # self.BUS_STATIONS.sort()
        print("Bus line steps = %d; Network edges = %d" % (len(self.BUS_LINE_STEPS), len(self.NETWORK_EDGES)))
        return

    def __init__(self, readfile="Schedule/test_busline.txt"):
        self.read_file = readfile
        self.process_file()
