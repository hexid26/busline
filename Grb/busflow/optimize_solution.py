#!/usr/bin/env python
# coding:utf-8
import copy
from gurobipy import Model, GRB, quicksum


def optimize(V, d, s, lam, lam_triple, pv, pc, T, P, p_list, v_to_next_v, v_to_pre_v):
    model = Model("bus-flow")

    xv = {}
    for v in V:
        xv[v] = model.addVar(vtype=GRB.BINARY, name='xv[%s]' % (v), lb=0)


    xpuv = {}
    for u in V:
        for v in V:
            for p in P:
                xpuv[p, u, v] = model.addVar(vtype=GRB.BINARY, name='xuv[%s, %s, %s]' % (p, u, v), lb=0)

    fuv = {}
    for u in V:
        for v in V:
            # if u != v:
            fuv[u, v] = model.addVar(vtype=GRB.CONTINUOUS, name='fuv[%s, %s]' % (u, v), lb=0)
            # fuv[u, v] = 0
    fuvw = {}
    for u in V:
        for v in V:
            for w in V:
                fuvw[u, v, w] = model.addVar(vtype=GRB.CONTINUOUS, name='fuvw[%s, %s, %s]' % (u, v, w), lb=0)
                # fuvw[u, v, w] = 0

    # bound 1
    for u in V:
        for v in V:
            if u != v:
                model.addConstr(fuv[u, v] <= s * d[u, v])

    # bound 2

    for u in V:
        for v in V:
            for p in P:
                if u != v and u == p_list[p][0] and v in p_list[p]:
                    model.addConstr(fuv[u, v] >= s * d[u, v] * (1 - xpuv[p, u, v]))

    # bound 3

    for u in V:
        for v in V:
            for w in v_to_next_v[v]:
                if u != w and w != v:
                    if lam_triple.get((u, v, w), -1) != -1:
                        model.addConstr(fuvw[u, v, w] <= s * lam_triple[u, v, w])

    # bound 4

    for u in V:
        for v in V:
            for p in P:
                for w in v_to_next_v[v]:
                    if u != w and w != v and u == p_list[p][0] and v in p_list[p]:
                        model.addConstr(fuvw[u, v, w] >= s * lam_triple[u, v, w] * (1 - xpuv[p, u, v]))

    for u in V:
        for v in V:
            for p in P:
                if u != v and u == p_list[p][0] and v in p_list[p]:
                    model.addConstr(
                        quicksum(xv[v] for x in p_list[p] if p_list[p].index(x) <= p_list[p].index(v))* 9999 >= xpuv[p, u, v]
                    )

                    model.addConstr(
                        quicksum(xv[v] for x in p_list[p] if p_list[p].index(x) <= p_list[p].index(v)) <= 9999 * xpuv[p, u, v]
                    )


    # bound 5
    for u in V:
        model.addConstr(lam[u] * s * (1 - xv[u]) == quicksum(fuvw[u, u, w] for w in v_to_next_v[u] if u != w))

    # bound 6.1

    for u in V:
        for v in V:
            if u != v:
                model.addConstr(
                    quicksum(fuvw[u, x, v] * (1 - xv[v]) for x in v_to_pre_v[v]) == fuv[u, v] + quicksum(
                        fuvw[u, v, w] for w in v_to_next_v[v] if u != w))

    # xv <= 2
    model.addConstr(quicksum(xv[v] for v in V) <= 2)


    # object 1
    # model.setObjective(
    #     quicksum(xv[v] * pv * T for v in V) +
    #     quicksum(T * pc * (lam[u] * s - lam[u] * s * xv[u] -
    #                        quicksum(quicksum(fuvw[u, x, v] * xv[v] for v in v_to_next_v[x] if u != v) for x in V)) for u
    #              in V if lam.get(u, -1) != -1),
    #     GRB.MINIMIZE)

    # object 3
    model.setObjective(quicksum(
        quicksum(quicksum(fuvw[u, x, v] * xv[v] for x in v_to_pre_v[v]) for u in V if u != v) + lam[v] * s * xv[v] for v
        in V),
        GRB.MAXIMIZE)

    model.params.OutputFlag = 0

    model.optimize()
    print model.status
    if model.status == GRB.status.OPTIMAL:
        print "Opt.value = ", model.ObjVal
        res = model.getVars()
        for i in res:
            if i.x < 0:
                print i.varName, i.x


def get_v_to_next_v(graph_dict, V):
    v_to_next_v = {}
    for u in V:
        v_to_next_v[u] = []
        for v in V:
            if graph_dict[u, v] == 1:
                v_to_next_v[u].append(v)

    return v_to_next_v


def get_v_to_pre_v(graph_dict, V):
    v_to_pre_v = {}
    for u in V:
        v_to_pre_v[u] = []
        for v in V:
            if graph_dict[v, u] == 1:
                v_to_pre_v[u].append(v)

    return v_to_pre_v

    pass


def get_puv(path, V):
    puv = {}
    for u in V:
        for v in V:
            puv[u, v] = 0

    # for p in path:

def get_p_list(path, P):
    p_list = {}
    for p in P:
        print path[P.index(p)]
        route_list = copy.deepcopy(path[P.index(p)])
        route_list.remove(route_list[0])
        p_list[p] = route_list
    return p_list


def start():
    V = ["v" + str(i) for i in range(1, 6)]

    s = 1
    pv = 500
    pc = 1
    T = 1

    graph = {}
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

    v_to_next_v = get_v_to_next_v(graph, V)
    v_to_pre_v = get_v_to_pre_v(graph, V)

    lam = {
        "v1": 200,
        "v2": 700,
        "v3": 100,
        "v4": 0,
        "v5": 1100
    }

    lam_triple = {}

    for u in V:
        for v in V:
            for w in V:
                lam_triple[u, v, w] = 0

    lam_triple["v1", "v1", "v4"] = 200

    lam_triple["v2", "v2", "v3"] = 400
    lam_triple["v2", "v3", "v4"] = 400
    lam_triple["v2", "v2", "v1"] = 300
    lam_triple["v2", "v1", "v4"] = 100

    lam_triple["v3", "v3", "v1"] = 100
    lam_triple["v3", "v1", "v4"] = 100

    lam_triple["v5", "v5", "v2"] = 500
    lam_triple["v5", "v5", "v3"] = 600
    lam_triple["v5", "v2", "v1"] = 200
    lam_triple["v5", "v3", "v1"] = 500
    lam_triple["v5", "v1", "v4"] = 200

    d = {}

    for u in V:
        for v in V:
            d[u, v] = 0

    d["v1", "v4"] = 200

    d["v2", "v1"] = 200
    d["v2", "v4"] = 500

    d["v3", "v4"] = 100

    d["v5", "v1"] = 500
    d["v5", "v2"] = 300
    d["v5", "v3"] = 100
    d["v5", "v4"] = 200

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

    P = ["p" + str(i) for i in range(1, len(path) + 1)]
    p_list = get_p_list(path, P)
    optimize(V, d, s, lam, lam_triple, pv, pc, T, P, p_list, v_to_next_v, v_to_pre_v)


start()
