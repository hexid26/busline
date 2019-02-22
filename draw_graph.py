#!/usr/bin/env python
# coding:utf-8
"""build_graph.py"""

import argparse
import logging
import networkx as nx
import matplotlib.pyplot as plt
from threading import Thread
from include.BusRoute import BusRoute


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


__logger__ = get_logger('build_graph')


def sort_edges(edge_list):
    """Sort the edges in edge_list

    Find out the one_way edges and the two_way edges

    Arguments:
        edge_list {[list]} -- the list including all edges to be sorted

    Returns:
        [list] -- one_way_edges_list
        [list] -- two_way_edges_list
    """
    one_way_edges_list = []
    two_way_edges_list = []
    for edge in edge_list:
        if (edge[1], edge[0]) not in edge_list:
            one_way_edges_list.append(edge)
        else:
            two_way_edges_list.append(edge)
    return one_way_edges_list, two_way_edges_list


def draw_graph(bus_route, pos_mode=0, top=[]):
    edge_list = bus_route.NETWORK_EDGES
    fig = plt.figure()
    graph = nx.DiGraph()
    color_list = []
    edges_1_list, edges_2_list = sort_edges(edge_list)
    graph.add_edges_from(edge_list)
    graph_tag = ''
    if pos_mode == 1:
        pos = nx.spring_layout(graph, k=1, iterations=3)
        graph_tag = '_spring'
    elif pos_mode == 2:
        print("Please input the id of fog nodes:")
        node_cnt = 0
        for node in bus_route.BUS_STATIONS:
            print("%d: %s" % (node_cnt, node))
            node_cnt += 1
        nodes_string = input("Input the id of fog nodes: ")
        nodes_list = nodes_string.split(',')
        for id_index in nodes_list:
            top.append(bus_route.BUS_STATIONS[int(id_index)])
        print(top)
        pos = nx.bipartite_layout(graph, top, align='horizontal')
        graph_tag = '_bipartite'
    else:
        graph_tag = '_kamada_kawai'
        pos = nx.kamada_kawai_layout(graph)
    # __logger__.debug(graph.edges().data('color'))
    for edge in graph.edges():
        if edge in edges_1_list:
            color_list.append('black')
        if edge in edges_2_list:
            color_list.append('red')
    # __logger__.debug(color_list)
    nx.draw_networkx_edges(
        graph, pos, edge_color=color_list, arrows=True, arrowsize=15)
    nx.draw_networkx_nodes(graph, pos, node_size=500, node_shape='o')
    nx.draw_networkx_labels(graph, pos)
    plt.xticks([])
    plt.yticks([])
    plt.axis('off')
    fig.tight_layout()
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    save_path = 'graph/' + ARGS.file[9:-4] + graph_tag + '.eps'
    plt.savefig(
        save_path,
        format='eps',
        frameon=False,
        pad_inches='tight',
        # bbox_inches='tight')
    )
    plt.close()


def main():
    """Main function"""
    __logger__.info('Process start!')
    bus_route = BusRoute(ARGS.file)
    draw_graph(bus_route, 0, [])
    draw_graph(bus_route, 1, [])
    draw_graph(bus_route, 2, [])
    __logger__.info('Process end!')


if __name__ == '__main__':
    # Uncomment the next line to read args from cmd-line
    ARGS = set_argparse()
    main()
