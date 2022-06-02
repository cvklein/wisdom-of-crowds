import networkx as nx
from collections import defaultdict
import itertools
from networkx.exception import NetworkXNoPath
import warnings
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import Normalize
from collections import Counter

class Crowd:
    """
    Class for encapsulating a graph and pre-computed (memoized) features for the
    Wisdom of Crowds algorithm, per Sullivan et al. (2020),
    
    "Vulnerability in Social Epistemic Networks" *International Journal of Philosophical Studies*
    https://doi.org/10.1080/09672559.2020.1782562
    
    Attributes:
        G: networkx graph (see __init__)
        min_k: smallest k to consider during processing, defaults to 2
        max_k: largest k to consider during processing, defaults to 5
        min_m: smallest m to consider during processing, defaults to 1
        max_m: largest m to consider during processing
        node_key: attribute to consider for each node (see __init__)        
        precomputed_path_dict: cache for unconditional paths
        precomputed_paths_by_hole_node: cache for dict of paths per node
        refresh_requested: flag indicating if cache has expired
        node_set: a snapshot of nodes to detect cache expiry
        edge_set: a snapshot of nodes to detect cache expiry
        s_cache: cached versions of S results
    """
    def __init__(self, G, max_m=5, node_key='T'):
        """
        Constructor:
            `__init__`: Inits the Crowd object.
        
        Args:
            G: a networkx graph, typically DiGraph.
            max_m: maximum m to consider in the calculations
            node_key: attribute to consider for each node, when considering topic diversity (defaults to 'T')
        """
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
        #cache S values too. This speeds up pi, and recalcs. cleared if you clear path dict.
        self.s_cache = {}


    def __efficient_pairs(self, x):
        """
        __efficient_pairs: internal function, makes search for possible cliques more efficient.
        
        This should not be called directly by the user.
        
        Args:
            x: input list
            
        Returns:
          unique pairs of elements (x_i, x_j)
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
        
        Args:
            v: vertex under exclusion
            source: source node
            target: target node
        
        Returns:
            integer z, in range 0 <= z < +infinity (unadjusted)
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

                if not (source in G_sub and target in G_sub):
                    # no path, as it doesn't exist anymore in the culled subgraph
                    self.precomputed_paths_by_hole_node[v][(source,target)] = []
                    return []
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
            
        Args:
            v: vertex under consideration, as defined by (Sullivan et al., 2020)
            source: source node
            target: target node
        
        Returns: 
            integer z, in range 0 <= z <= +infinity
        """
        z = len(self.__shortest_path_node_source_target(v, source, target))
        if z == 0:
            return(float('inf'))
        else:
            #z-1 because the path is a list of nodes incl start and end ; we're using distance=number of edges, which is 1 less.
            return z - 1


    def is_mk_observer(self, v, m, k):
        """
        is_mk_observer: checks if the vertex v is an (m,k)-observer as defined by (Sullivan et al., 2020);
            optimized clique-finding algo by CVK.
        
        Args:
            v: vertex to evaluate
            m: m as defined in (Sullivan et al., 2020); m >= 1
            k: k as defined in (Sullivan et al., 2020); k > 1
        
        Returns:
            a boolean indicating the m,k-observer status of v
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

        if self.G.is_directed():
            source_nodes = list(self.G.predecessors(v))
        else:
            source_nodes = list(self.G.neighbors(v))

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
        S: calculates S, defined in (Sullivan et al., 2020) as the structural position of v. 
        
            S = max_{(m,k) in MK}(m * k)
            
        Args:
            v: vertex to evaluate
            
        Returns:
            integer S, in range 0 <= (class constant max_m * class constant max_k)
        """

        try:
            s  = self.s_cache[v]
            return s 
        except KeyError:
            pass


        possibilities = sorted([(m*k, m, k) for m, k in \
            itertools.product(range(self.min_m, self.max_m+1), \
                              range(self.min_k, self.max_k+1))], \
            reverse=True)

        for mk, m, k in possibilities:
            mk_observer = self.is_mk_observer(v, m, k)
            if mk_observer:
                self.s_cache[v] = mk
                return mk
            else:
                pass

        self.s_cache[v] = 0
        return 0


    def D(self, v):
        """
        D: calculates D, defined in the literature as the number of topics found for
            informants of vertex v per (Sullivan et al., 2020)
            
            We apply the general case D = D' = | union_{(u,v) in E} C'(u) |
            
        Args:
            v: vertex to evaluate
        
        Returns:
            integer D, in range 0 <= D
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
        
        Args:
            v: vertex to evaluate
            
        Returns:
            integer pi, where pi = S * D
        """
        return self.D(v) * self.S(v)


    def h_measure(self, v, max_h=6):
        """
        h_measure: find the highest h, given vertex v, of which mk_observer(v, h, h) is true
        
        Args:
            v: vertex to evaluate
            max_h: maximum_h to evaluate, defaults to 6 per (Sullivan et al., 2020)
        
        Returns:
            integer h, in range 1 < h <= max_h
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
        self.s_cache = {}
        self.refresh_requested = True
        return


"""
Now we add some additional utility/helper functions that are public-facing
These can be called by importing them
    from wisdom_of_crowds import make_sullivanplot
    from wisdom_of_crowds import iteratively_prune_graph
"""

def make_sullivanplot(pis, ds, ses, colormap='gist_yarg', suptitle=None, cax=None, yscale='linear'):
    """
    make_sullivanplot: This makes the style of plot from Sullivan et al (2020).
    
    cvk note: Could be more generic, but essentially has two modes:
        
    * One, you can just pass a list of pis, Ds, and Ses, optionally with a colormap and a suptitle.
      This will make and render a plot
      
    * Two, or else you can pass an axis (and optionally colormap and suptitle)
      and this will render it on the axis, allowing for multiple plots (as done in the paper figures).

    Args:
        pis: a list of pi-s
        ds:  a list of D-s
        ses: a list of S-s
        colormap: (optional) name of a colormap, defaults to 'gist_yarg'
        suptitle: (optional) supplementary title
        cax:  (optional) axis to render on
        yscale: (optional) scale of y-axis. Defaults to linear.
    
    Precondition:
        PRECONDITION: len(pis) == len(Ds) == len(Ses) == X, where len(X) > 0

    Returns:
        None on success; but generates the plot in a plt window.
    """
    assert(len(pis) == len(ds) == len(ses))
    assert(len(pis) > 0)

    cmap = plt.get_cmap(colormap)
    norm = Normalize(vmin=min(ds)-1,vmax=max(ds)+1)

    # sort by pi, then d
    z = sorted([(pi,d,s) for pi,d,s in zip(pis,ds,ses)])
    pis = [pi for pi,d,s in z]
    sds = [(s,d) for pi,d,s in z]

    # make the pi values first
    total = len(pis)
    c = Counter(pis)
    cumulative = 0

    xs = [0]
    ys = [0]

    for pi in c:
        xs.append(cumulative)
        ys.append(ys[-1])
        xs.append(cumulative)
        ys.append(pi)
        cumulative += c[pi] / total


    # now build up the bar graph
    sdcounter = Counter(sds)
    total = len(pis)
    current_x = 0
    cumulative = 0

    barx = []
    barwidth = []
    barheight = []
    barcolors = []
    seen = []
    for pi,d,s in z:
        if (pi,s,d) in seen:
            pass
        else:
            barx.append(current_x)

            cumulative += (sdcounter[(s,d)]/total)
            current_x = cumulative

            barwidth.append(sdcounter[(s,d)]/total)
            barheight.append(s)
            barcolors.append(cmap(norm(d)))
            seen.append((pi,s,d))

    # do the plot
    if cax == None:
        fig = plt.figure(figsize=(12,6),facecolor='w')
        ax = fig.add_subplot(111)
    else:
        ax = cax

    ax.bar(barx,barheight,width=barwidth,color=barcolors,align='edge')
    ax.plot(xs,ys,c='k')

    ax.set_xticks([0,0.2,0.4,0.6,0.8,1.0])
    ax.set_xlim((0,1))

    ax.yaxis.tick_right()
    ax.yaxis.grid()

    # make the legend for D
    handles = []
    for d in set(ds):
        handles.append(mpatches.Patch(color=cmap(norm(d)), label="D="+str(d)))
    ax.legend(handles=handles,loc='upper left')

    ax.set_yscale(yscale)

    if suptitle is not None:
        ax.set_title(suptitle)

    if cax==None:
        plt.show()
        return None
        ax.set_xlabel('Proportion')
        ax.set_ylabel('S/pi')
    else:
        return None


def iteratively_prune_graph(H, threshold=1, weight_threshold=None, weight_key='weight', verbose=False):
    """
    iteratively_prune_graph: Iterative graph pruner, provided as a helper function.
    
    With no arguments, it iteratively prunes as per Sullivan et al (2020).
    i.e. culls all nodes with indegree + outdegree <= 1, takes the largest connected component, and iterates until stable.
    It also adds the possibility of a weight threshold, which is useful for bigger/denser graphs.
    cvk note: I ended up making a copy b/c in-place destructive changes are easier than playing with subgraphs

    Args:
        H: source graph - will not be modified. [NB: this is nx.Graph; NOT Crowd. An assertion will test for this.]
        threshold: (optional) threshold T where indegree+outdegree <= T
        weight_threshold: (optional) allows specification of weights-per-edge. This throws an exception if edges are not weighted
        weight_key: (optional) identifies key used for weight thresholding. Ignored if weight_threshold is not specified.
        verbose: (optional) debugging flag for verbose reporting
        
    Returns:
        G: pruned graph, which is a full (deep) copy of H then pruned.
    """
    if not isinstance(H, nx.Graph):
        raise TypeError('The helper function iteratively_prune_graph expects a Graph, not Crowd.')

    G = H.copy() #make a copy rather than editing in place
    done = False
    iteration = 0

    if verbose:
        print(f'[iteratively_prune_graph: threshold={threshold}, weight_threshold={weight_threshold}, verbose.]')

    while not done:
        iteration += 1
        done = True
        if verbose:
            print(f'\n\nIteration #{iteration}...')
            print('================================')
            print(len(G.nodes),len(G.edges))
        nodes_to_cut = []

        # this part directly from paper
        # but accomodate directed and undirected
        if G.is_directed():
            for node in G:
                i = G.in_degree(node)
                o = G.out_degree(node)
                if i + o <= threshold:
                    nodes_to_cut.append(node)
        else:
            for node in G:
                d = G.degree(node)
                if d <= threshold:
                    nodes_to_cut.append(node)

        if len(nodes_to_cut) > 0:
            done = False
            G.remove_nodes_from(nodes_to_cut)

        # then do the weighted-edge culling
        if weight_threshold == None:
            pass
        else:
            edges_to_cut = []
            for edge in G.edges:
                try:
                    if G.edges[edge][weight_key] <= weight_threshold:
                        edges_to_cut.append(edge)
                except KeyError:
                    raise KeyError('Weight attribute for thresholding not present; failing.')

            if len(edges_to_cut) > 0:
                done = False
                G.remove_edges_from(edges_to_cut)

        # now greatest connected component - only one difference between graph and digraph: i.e. to squash digraph.
        if not done:
            if G.is_directed():
                T = nx.Graph(G) # squash to undirected if necessary, b/c not defined for directed.
            else:
                T = G

            Gcc = sorted(nx.connected_components(T), key=len, reverse=True)
            try:
                G = nx.Graph(G.subgraph(Gcc[0]))
            except IndexError:  # you have pruned away your graph, return a null graph rather than choke
                return nx.generators.classic.null_graph()
    return G
