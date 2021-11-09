import networkx as nx
from collections import defaultdict
import itertools
from networkx.exception import NetworkXNoPath
import warnings

class Crowd:
    """ 
    Class for encapsulating a graph and pre-computed (memoized) features for the 
    Wisdom of Crowds algorithm, per Sullivan et al. (2020),
    "Vulnerability in Social Epistemic Networks" *International Journal of Philosophical Studies* 
    https://doi.org/10.1080/09672559.2020.1782562
    :param G: a networkx graph, typically DiGraph.
    :param max_m: maximum m to consider in the calculations
    :param node_key: attribute to consider for each node, when considering topic diversity (defaults to 'T')
    """
    def __init__(self, G, max_m=5, node_key='T'):
        # object check to avoid null ptr reference
        if G is None:
            raise ValueError('Crowd: init requires a valid networkx graph!')
        self.G = G
        self.min_k = 2
        self.max_k = 5
        self.min_m = 1
        self.max_m = max_m
        self.node_key = node_key
        self.precomputed_path_dict = {} # holds unconditional paths
        self.precomputed_paths_by_hole_node = defaultdict(dict)  # holds dict of paths per node
        self.refresh_requested = False

        # if G is okay, we 'hash' the graph data to prevent external updates breaking internal caches
        # NB: weisfeiler_lehman_graph_hash(G) is the best, but is very performance-draining
        self.node_set = set(G.nodes())
        self.edge_set = set(G.edges())  

    def __efficient_pairs(self, x):
        """
        __efficient_pairs: internal function, makes search for possible cliques more efficient.
            This should not be called directly by the user.
        :param x: input list
        :returns: unique pairs of elements (x_i, x_j)
        """
        l = len(x)
        for i in range(1, l):
            for j in range(0, i):
                yield (x[i], x[j])


    def __shortest_path_node_source_target(self, v, source, target):
        """
        __shortest_path_node_source_target: internal function,
            to get the length of the shortest path between vertices source and target, excluding v. 
            The results need to be postprocessed by wrapper function 
            shortest_path_length_node_source_target and not called directly.
            This function does memoization for efficient future processing:
            for a single node, and a single source, precompute the path,
            and populate the current dictionary precomputed_path_dict with them.
        :param v: vertex under exclusion
        :param source: source node
        :param target: target node
        :returns: integer z, in range 0 <= z < +infinity (unadjusted)
        """
        # error checking: 'v' needs to exist. 
        # (missing 'source' and 'target' raised by nx)
        if v not in nx.nodes(self.G):
            raise nx.NodeNotFound

        # step 1: am I in the generic path dictionary? (memoized)
        try:
            shortest_unconditional_path = self.precomputed_path_dict[(source,target)]
        except KeyError: #well figure this later in case it comes in handy
            try:
                shortest_unconditional_path = nx.algorithms.shortest_path(self.G,source,target)
                self.precomputed_path_dict[(source,target)] = shortest_unconditional_path
            except NetworkXNoPath:
                shortest_unconditional_path = []
                self.precomputed_path_dict[(source,target)] = shortest_unconditional_path
                for x in range(1,len(shortest_unconditional_path)-1):
                    z = shortest_unconditional_path[x:]
                    self.precomputed_path_dict[(z[1],target)] = z

        # step 2 check if this is also a path without the node of interest
        if v not in shortest_unconditional_path:
            return shortest_unconditional_path
        # now we have to find the shortest path in a subgraph without the node of interest    
        else: 
            try:
                shortest_conditional_path = self.precomputed_paths_by_hole_node[v][(source,target)]
                return shortest_conditional_path
            except KeyError:
                nodes_less_v = self.node_set - set([v])
                G_sub = self.G.subgraph(nodes_less_v)
                try:
                    shortest_conditional_path = nx.algorithms.shortest_path(G_sub,source,target)
                    # note that subpaths could also be cached as per above
                    self.precomputed_paths_by_hole_node[v][(source,target)] = shortest_conditional_path
                    return shortest_conditional_path
                except NetworkXNoPath:
                    self.precomputed_paths_by_hole_node[v][(source,target)] = []
                    return []

    
    def shortest_path_length_node_source_target(self, v, source, target):
        """
        shortest_path_length_node_source_target: wrapper function to get the length of the
            shortest path between vertices source and target, without vertex v. 
            no path = infinite length
        :param v: vertex under consideration, as defined by (Sullivan et al., 2020)
        :param source: source node
        :param target: target node
        :returns: integer z, in range 0 <= z <= +infinity
        """
        z = len(self.__shortest_path_node_source_target(v, source, target))
        if z == 0:
            return(float('inf'))
        else:
            #z-1 because the path is a list of nodes incl start and end ; we're using distance=number of edges, which is 1 less. 
            return z - 1 


    def is_mk_observer(self, v, m, k):
        """
        is_mk_observer: checks if the vertex v is an (m,k)-observer as defined by (Sullivan et al., 2020)
            optimized clique-finding algo by CVK
        :param v: vertex to evaluate
        :param m: m as defined in (Sullivan et al., 2020); m >= 1
        :param k: k as defined in (Sullivan et al., 2020); k > 1
        :returns: boolean 
        """
        if m < 1 or k <= 1:
            raise ValueError('Crowd: m needs to be integer >= 1; k needs to be integer > 1.')
        
        # PRECONDITION 1: if original graph seems to be 'obsolete', 
        if set(nx.nodes(self.G)) != self.node_set or set(nx.edges(self.G)) != self.edge_set:
            # and PRECONDITION 2: AND ONLY IF the user fails to call clear_path_dict...
            if not self.refresh_requested:
                # throw error and hint as to how user can fix this by regenerating all intermediate data
                warnings.warn('Performance warning: modifying G externally will result in "cache misses"; please refactor your code to avoid external modification, and to handle LookupErrors.')
                raise LookupError('Crowd: graph G has been modified externally, cached precomputed_path_dict is obsolete and need to be regenerated! Suggest using crowd.clear_path_dict()')
            else:
                # rehash the nodeset and edgeset so the graph is no longer detected as "changed"
                # i.e. on next run, the graph is considered "stable" and there is no need to request a refresh
                self.node_set = set(self.G.nodes())
                self.edge_set = set(self.G.edges())  

                # user has confirmed that the cache has indeed been cleared.
                assert self.precomputed_path_dict == {}
                assert len(self.precomputed_paths_by_hole_node) == 0
                # disable the error detector for future runs (until the graph is tampered-with, again)
                self.refresh_requested = False

        source_nodes = list(self.G.predecessors(v))

        # if you have fewer than k, then you can't hear from at least k
        if len(source_nodes) < k: 
            return False

        # special case, to ensure that a node with one input is a 1,1 observer
        if (len(source_nodes) == 1) and k==1 and m==1: 
            return True

        max_k_found = False
        clique_dict = defaultdict(list) # this will get used to look for cliques

        # helper method __efficient_pairs makes sure that cliques are found and 
        # early termination happens as soon as possible
        for source_a,source_b in self.__efficient_pairs(source_nodes):
            a_path_length = self.shortest_path_length_node_source_target(v,source_a,source_b)
            b_path_length = self.shortest_path_length_node_source_target(v,source_b,source_a)

            # if shortest path is too short, keep looking
            if (a_path_length<m) or (b_path_length<m): 
                pass

            else:  # now we do the clique updating
                # first each pair trivially forms a clique
                # pairs are unique so we don't have to double-check as we go (i hope!)

                # first, this check is needed because if k<=2 then any hit at all satisfies it;
                # and it's time to go home
                if k<=2:
                    return True

                trivial_clique = set([source_a,source_b])
                clique_dict[source_a].append(trivial_clique)
                clique_dict[source_b].append(trivial_clique)


            # now, for each pair of cliques for the two nodes, we have a new clique iff:
            # each clique has the same size m
            # the set containing the union of nodes from the two pairs of m-sized cliques is size m+1
            # so check the cliques in the nodes connected by the new pair
                for a, b in itertools.product(clique_dict[source_a], clique_dict[source_b]):
                    lena = len(a)
                    lenb = len(b)
                    if lena != lenb:
                        pass
                    # avoid double counting
                    # thogh you can probably do this faster by not adding the trivial clique until later?
                    elif (a == trivial_clique) or (b == trivial_clique):
                        pass
                    else:
                        node_union = a | b
                        lenu = len(node_union)
                        if lenu == (lena + 1):
                            if lenu >= k:  # early termination
                                max_k_found = True
                                return max_k_found
                            else:
                                for node in node_union:
                                    clique_dict[node].append(node_union)
        return max_k_found


    def S(self, v):
        """
        S: calculates S, defined in (Sullivan et al., 2020) as the structural position of v
            S = max_{(m,k) in MK}(m * k)
        :param v: vertex to evaluate
        :returns: integer S, in range 0 <= (class constant max_m * class constant max_k) 
        """
        possibilities = sorted([(m*k, m, k) for m, k in \
            itertools.product(range(self.min_m, self.max_m+1), \
                              range(self.min_k, self.max_k+1))], \
            reverse=True)
        
        for mk, m, k in possibilities:
            mk_observer = self.is_mk_observer(v, m, k)
            if mk_observer:
                return mk
            else:
                pass
        return 0


    def D(self, v):
        """
        D: calculates D, defined in the literature as the number of topics found for
            informants of vertex v per (Sullivan et al., 2020)
            We apply the general case D = D' = | union_{(u,v) in E} C'(u) |
        :param v: vertex to evaluate
        :returns: integer D, in range 0 <= D 
        """
        topics = set()
        source_nodes = self.G.predecessors(v)

        for s in source_nodes:
            s_topic = self.G.nodes[s][self.node_key]
            if type(s_topic) == set:
                topics.update(s_topic)
            else:
                topics.add(s_topic)

        return len(topics)


    def pi(self, v):
        """
        pi: calculates pi, given vertex v, defined in (Sullivan et al., 2020) as the product of S and D
        :param v: vertex to evaluate
        :returns: integer pi, where pi = S * D
        """
        return self.D(v) * self.S(v)


    def h_measure(self, v, max_h=6):
        """
        h_measure: find the highest h, given vertex v, of which mk_observer(v, h, h) is true
        :param v: vertex to evaluate
        :param max_h: maximum_h to evaluate, defaults to 6 per (Sullivan et al., 2020)
        :returns: integer h, in range 1 < h <= max_h
        """
        for h in range(max_h, 1, -1): # recall (k > 1) 
            if self.is_mk_observer(v, h, h):
                return h
        return 0
    
    def clear_path_dict(self):
        """
        clear_path_dict: helper function to completely reset the precomputed path dictionary. 
        Should be used if G is changed. 
        """
        self.precomputed_path_dict = {} 
        self.precomputed_paths_by_hole_node = defaultdict(dict)  
        self.refresh_requested = True
        return 