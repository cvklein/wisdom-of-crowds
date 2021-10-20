Module wisdom_of_crowds
=======================

Classes
-------

`Crowd(G, max_m=5, node_key='T')`
:   Class for encapsulating a graph and pre-computed (memoized) features for the 
    Wisdom of Crowds algorithm, per Sullivan et al. (2020),
    "Vulnerability in Social Epistemic Networks" *International Journal of Philosophical Studies* 
    https://doi.org/10.1080/09672559.2020.1782562
    :param G: a networkx graph, typically DiGraph.
    :param max_m: maximum m to consider in the calculations
    :param node_key: attribute to consider for each node, when considering topic diversity (defaults to 'T')

    ### Methods

    `D(self, v)`
    :   D: calculates D, defined in the literature as the number of topics found for
            informants of vertex v per (Sullivan et al., 2020)
            We apply the general case D = D' = | union_{(u,v) in E} C'(u) |
        :param v: vertex to evaluate
        :returns: integer D, in range 0 <= D

    `S(self, v)`
    :   S: calculates S, defined in (Sullivan et al., 2020) as the structural position of v
            S = max_{(m,k) in MK}(m * k)
        :param v: vertex to evaluate
        :returns: integer S, in range 0 <= (class constant max_m * class constant max_k)

    `h_measure(self, v, max_h=6)`
    :   h_measure: find the highest h, given vertex v, of which mk_observer(v, h, h) is true
        :param v: vertex to evaluate
        :param max_h: maximum_h to evaluate, defaults to 6 per (Sullivan et al., 2020)
        :returns: integer h, in range 1 <= h <= max_h

    `is_mk_observer(self, v, m, k)`
    :   is_mk_observer: checks if the vertex v is an (m,k)-observer as defined by (Sullivan et al., 2020)
            optimized clique-finding algo by CVK
        :param v: vertex to evaluate
        :param m: m as defined in (Sullivan et al., 2020)
        :param k: k as defined in (Sullivan et al., 2020)
        :returns: boolean

    `pi(self, v)`
    :   pi: calculates pi, given vertex v, defined in (Sullivan et al., 2020) as the product of S and D
        :param v: vertex to evaluate
        :returns: integer pi, where pi = S * D

    `shortest_path_length_node_source_target(self, v, source, target)`
    :   shortest_path_length_node_source_target: wrapper function to get the length of the
            shortest path between vertices source and target, without vertex v. 
            no path = infinite length
        :param v: vertex under consideration, as defined by (Sullivan et al., 2020)
        :param source: source node
        :param target: target node
        :returns: integer z, in range 0 <= z <= +infinity
