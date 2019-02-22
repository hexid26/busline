#!/usr/bin/env python
# coding:utf-8
import copy
# from gurobipy import Model, GRB, quicksum
from gurobipy import Model, GRB, quicksum

def optimize(dpuv, lam, lam_triple, s, P, V, p_v_to_next_v, p_v_to_pre_v, p_list):
    model = Model("bus-flow")

    xv = {}
    for v in V:
        xv[v] = model.addVar(vtype=GRB.BINARY, name='xv[%s]' % (v), lb=0)

    xpuv = {}
    for u in V:
        for v in V:
            for p in P:
                xpuv[p, u, v] = model.addVar(vtype=GRB.BINARY, name='xpuv[%s, %s, %s]' % (p, u, v), lb=0)

    fpuv = {}
    for u in V:
        for v in V:
            for p in P:
                fpuv[p, u, v] = model.addVar(vtype=GRB.CONTINUOUS, name='fpuv[%s, %s, %s]' % (p, u, v), lb=0)

    fpuvw = {}
    for u in V:
        for v in V:
            for w in V:
                for p in P:
                    fpuvw[p, u, v, w] = model.addVar(vtype=GRB.CONTINUOUS, name='fpuvw[%s, %s, %s, %s]' % (p, u, v, w),
                                                     lb=0)

    # bound 1
    for u in V:
        for v in V:
            for p in P:
                if u in p_list[p] and v in p_list[p] and p_list[p].index(u) == 0 and u != v:
                    model.addConstr(fpuv[p, u, v] <= dpuv[p, u, v] * s)
    # bound 2
    for u in V:
        for v in V:
            for p in P:
                if u in p_list[p] and v in p_list[p] and p_list[p].index(u) == 0 and u != v:
                    model.addConstr(fpuv[p, u, v] >= dpuv[p, u, v] * s * (1 - xpuv[p, u, v]))

    # bound 3
    for u in V:
        for v in V:
            for p in P:
                for w in p_v_to_next_v[p, v]:
                    if u != w and w != v and u in p_list[p] and v in p_list[p] and p_list[p].index(u) == 0:
                        model.addConstr(fpuvw[p, u, v, w] <= s * lam_triple[p, u, v, w])

    # bound 4
    for u in V:
        for v in V:
            for p in P:
                for w in p_v_to_next_v[p, v]:
                    if u != w and w != v and u in p_list[p] and v in p_list[p] and p_list[p].index(u) == 0:
                        model.addConstr(fpuvw[p, u, v, w] >= s * lam_triple[p, u, v, w] * (1 - xpuv[p, u, v]))

    # bound 5
    for u in V:
        for p in P:
            if u in p_list[p] and p_list[p].index(u) == 0:
                model.addConstr(lam[p, u] * s * (1 - xv[u]) == quicksum(
                    fpuvw[p, u, u, w] for w in p_v_to_next_v[p, u] if u != w))

    # bound 6
    for u in V:
        for v in V:
            for p in P:
                if u in p_list[p] and v in p_list[p] and p_list[p].index(u) == 0 and u != v:
                    model.addConstr(
                        quicksum(fpuvw[p, u, x, v] * (1 - xv[v]) for x in p_v_to_pre_v[p, v]) ==
                        fpuv[p, u, v] + quicksum(fpuvw[p, u, v, w] for w in p_v_to_next_v[p, v])
                    )

    # bound 7
    for u in V:
        for v in V:
            for p in P:
                if u in p_list[p] and v in p_list[p] and p_list[p].index(u) == 0 and u != v:
                    model.addConstr(
                        quicksum(xv[n] for n in p_list[p] if p_list[p].index(n) <= p_list[p].index(v)) * 9999 >= xpuv[p, u, v]
                    )

                    model.addConstr(
                        quicksum(xv[n] for n in p_list[p] if p_list[p].index(n) <= p_list[p].index(v)) <= xpuv[p, u, v] * 9999
                    )

    xv <= 2
    model.addConstr(quicksum(xv[v] for v in V) <= 2)

    # object
    # for u in V:
    #     for v in V:
    #         for p in P:
    #             if u in p_list[p] and v in p_list[p] and p_list[p].index(u) == 0 and u != v and p_list[p].index(v) == len(p_list[p]) - 1:
    model.setObjective(quicksum(xpuv[p, u, v] * dpuv[p, u, v] for u in V for v in V for p in P if u in p_list[p] and v in p_list[p] and p_list[p].index(u) == 0 and u != v and p_list[p].index(v) == len(p_list[p]) - 1), GRB.MAXIMIZE)

    model.params.OutputFlag = 0

    model.optimize()
    print(model.status)
    if model.status == GRB.status.OPTIMAL:
        print("Opt.value = ", model.ObjVal)
        res = model.getVars()
        for i in res:
            if i.x > 0:
                print(i.varName, i.x)


def get_p_list(path, P):
    p_list = {}
    for p in P:
        route_list = copy.deepcopy(path[P.index(p)])
        route_list.remove(route_list[0])
        p_list[p] = route_list
    return p_list

def get_p_v_to_next_v(graph, path, V, P):
    p_v_to_next_v = {}
    for v in V:
        for p in P:
            p_v_to_next_v[p, v] = []
            route_list = copy.deepcopy(path[P.index(p)])
            for u in V:
                if graph[v, u] == 1 and u in route_list:
                    p_v_to_next_v[p, v].append(u)
    return p_v_to_next_v


def get_p_v_to_pre_v(graph, path, V, P):
    p_v_to_pre_v = {}
    for v in V:
        for p in P:
            p_v_to_pre_v[p, v] = []
            route_list = copy.deepcopy(path[P.index(p)])
            for u in V:
                if graph[u, v] == 1 and u in route_list:
                    p_v_to_pre_v[p, v].append(u)
    return p_v_to_pre_v

def get_lam(path, P, V):
    lam = {}
    for p in P:
        for v in V:
            if v == path[P.index(p)][1]:
                lam[p, v] = path[P.index(p)][0]
            else:
                lam[p, v] = 0
    return lam

def get_dpuv(path, V, P):
    dpuv = {}
    for u in V:
        for v in V:
            for p in P:
                if path[P.index(p)][1] == u and path[P.index(p)][len(path[P.index(p)]) - 1] == v:
                    dpuv[p, u, v] = path[P.index(p)][0]
                else:
                    dpuv[p, u, v] = 0
    return dpuv

def get_lam_triple(path, V, P):

    lam_triple = {}

    for u in V:
        for v in V:
            for w in V:
                for p in P:
                    lam_triple[p, u, v, w] = 0

    for p in P:
        route_list = copy.deepcopy(path[P.index(p)])
        route_list.remove(route_list[0])
        for i in range(len(route_list) - 1):
            lam_triple[p, route_list[0], route_list[i], route_list[i + 1]] = path[P.index(p)][0]

    return lam_triple


def start():
    path = [
        [300, "v5", "v2"],
        [200, "v5", "v2", "v1", "v4"],
        [500, "v5", "v3", "v1"],
        [100, "v5", "v3"],
        [400, "v2", "v3", "v4"],
        [200, "v2", "v1"],
        [100, "v2", "v1", "v4"],
        [100, "v3", "v1", "v4"],
        [200, "v1", "v4"]
    ]
    v_num = 5
    graph = {}

    P = ["p" + str(i) for i in range(1, len(path) + 1)]
    V = ["v" + str(i) for i in range(1, v_num + 1)]

    for u in V:
        for v in V:
            graph[u, v] = 0
    graph["v5", "v2"] = 1
    graph["v5", "v3"] = 1
    graph["v2", "v3"] = 1
    graph["v3", "v4"] = 1
    graph["v2", "v1"] = 1
    graph["v3", "v1"] = 1
    graph["v1", "v4"] = 1

    dpuv = get_dpuv(path, V, P)
    p_v_to_next_v = get_p_v_to_next_v(graph, path, V, P)
    p_v_to_pre_v = get_p_v_to_pre_v(graph, path, V, P)

    p_list = get_p_list(path, P)
    lam = get_lam(path, P, V)
    lam_triple = {}

    for u in V:
        for v in V:
            for w in V:
                lam_triple[u, v, w] = 0

    lam_triple = get_lam_triple(path, V, P)
    s = 1
    optimize(dpuv, lam, lam_triple, s, P, V, p_v_to_next_v, p_v_to_pre_v, p_list)

start()