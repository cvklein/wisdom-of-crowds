import pytest
import warnings
import networkx as nx
import wisdom_of_crowds as woc
import matplotlib

def test_init():
    # check that one error was raised
    with pytest.raises(ValueError):
        c = woc.Crowd(None)

    # defaults
    G = nx.Graph()
    c = woc.Crowd(G)
    assert c.G == G
    assert c.min_k == 2
    assert c.max_k == 5
    assert c.min_m == 1
    assert c.max_m == 5
    assert c.node_key == 'T'
    assert c.precomputed_path_dict == {} # holds unconditional paths
    assert c.precomputed_paths_by_hole_node == {}  # holds dict of paths per node
    assert c.node_set == set(G.nodes())

    # optional params
    G = nx.Graph()
    c = woc.Crowd(G, max_m=8, node_key="WWW")
    assert c.G == G
    assert c.min_k == 2
    assert c.max_k == 5
    assert c.min_m == 1
    assert c.max_m == 8
    assert c.node_key == 'WWW'
    assert c.precomputed_path_dict == {} # holds unconditional paths
    assert c.precomputed_paths_by_hole_node == {}  # holds dict of paths per node
    assert c.node_set == set(G.nodes())


def test__efficient_pairs():
    G = nx.Graph()
    c = woc.Crowd(G) # default with generic empty graph, minimum test case

    actual = c._Crowd__efficient_pairs([0,1,2]) # private method, need special accessor notation
    expected_pairs = [(1,0),(2,0),(2,1)]
    for i in expected_pairs:
        assert i == next(actual)


def test__shortest_path_node_source_target():
    c = __construct_test_crowd_4nodes_linkedlist()
    # case: a->b->c->d, exclude a. b to c = b->c
    assert c._Crowd__shortest_path_node_source_target('a','b','c') == ['b','c']
    # case: a->b->c->d, exclude a. b to d = b->c->d
    assert c._Crowd__shortest_path_node_source_target('a','b','d') == ['b','c','d']
    # case: a->b->c->d, exclude b. a to d = a->???unreachable???
    assert c._Crowd__shortest_path_node_source_target('b','a','d') == []

    # new instance, recreate the Crowd: avoids intermediate updates of the Crowd
    c = __construct_test_crowd_5nodes_shortcut()
    # case: a->b->c->d->e (shortcut a->e), exclude b. a to e = a->e via shortcut
    assert c._Crowd__shortest_path_node_source_target('b','a','e') == ['a','e']
    # case: a->b->c->d<->e (shortcut a->e), exclude b. a to d = a->e->d via shortcut and reverse edge
    assert c._Crowd__shortest_path_node_source_target('b','a','d') == ['a','e','d']

    # case: test warning and cache fallback warning system - i.e. modify an existing Graph post-creation
    # DEPRECATED SINCE COMMIT 20211103: Shifted the precondition check to mk_observer code...
    # c = __construct_test_crowd_ab_only()
    # with pytest.warns(Warning, match='Performance warning'):
    #     c.G.add_edge('x','y')
    #     c._Crowd__shortest_path_node_source_target('b','x','y')

    # case: no such node(s), expect nx.NodeNotFound to be raised by either Crowd or Graph
    c = __construct_test_crowd_ab_only()
    with pytest.raises(nx.NodeNotFound):
        c._Crowd__shortest_path_node_source_target('missing','a','b')
    with pytest.raises(nx.NodeNotFound):
        c._Crowd__shortest_path_node_source_target('a','missing','b')
    with pytest.raises(nx.NodeNotFound):
        c._Crowd__shortest_path_node_source_target('a','b','missing')
    
    # case: regression found 2 June 2022
    # in some edge cases, v=T or v=S, which crashes; should return [] as the path (no feasible path)
    assert c._Crowd__shortest_path_node_source_target('a','a','b') == []
    assert c._Crowd__shortest_path_node_source_target('a','b','a') == []
    assert c._Crowd__shortest_path_node_source_target('a','a','a') == []


def test_shortest_path_length_node_source_target():
    # see test__shortest_path_node_source_target for actual list contents...
    c = __construct_test_crowd_4nodes_linkedlist()
    # case: a->b->c->d, exclude a. b to c = b->c
    assert c.shortest_path_length_node_source_target('a','b','c') == 1
    # case: a->b->c->d, exclude a. b to d = b->c->d
    assert c.shortest_path_length_node_source_target('a','b','d') == 2
    # case: a->b->c->d, exclude b. a to d = a->???unreachable???
    assert c.shortest_path_length_node_source_target('b','a','d') == float('inf')

    # new instance, recreate the Crowd: avoids intermediate updates of the Crowd
    c = __construct_test_crowd_5nodes_shortcut()
    # case: a->b->c->d->e (shortcut a->e), exclude b. a to e = a->e via shortcut
    assert c.shortest_path_length_node_source_target('b','a','e') == 1
    # case: a->b->c->d<->e (shortcut a->e), exclude b. a to d = a->e->d via shortcut and reverse edge
    assert c.shortest_path_length_node_source_target('b','a','d') == 2

    # case: test warning and cache fallback warning system - i.e. modify an existing Graph post-creation
    # DEPRECATED SINCE COMMIT 20211103: Shifted the precondition check to mk_observer code...
    # c = __construct_test_crowd_ab_only()
    # with pytest.warns(Warning, match='Performance warning'):
    #     c.G.add_edge('x','y')
    #     c.shortest_path_length_node_source_target('b','x','y')

    # case: no such node(s), expect nx.NodeNotFound to be raised by either Crowd or Graph
    c = __construct_test_crowd_ab_only()
    with pytest.raises(nx.NodeNotFound):
        c.shortest_path_length_node_source_target('missing','a','b')
    with pytest.raises(nx.NodeNotFound):
        c.shortest_path_length_node_source_target('a','missing','b')
    with pytest.raises(nx.NodeNotFound):
        c.shortest_path_length_node_source_target('a','b','missing')

    # case: regression found 2 June 2022
    # in some edge cases, v=T or v=S, which crashes. should return +inf (no feasible path)
    assert c.shortest_path_length_node_source_target('a','a','b') == float('inf')
    assert c.shortest_path_length_node_source_target('a','b','a') == float('inf')
    assert c.shortest_path_length_node_source_target('a','a','a') == float('inf')


def __construct_test_crowd_ab_only():
    DG = nx.DiGraph()
    DG.add_edge('a','b')
    c = woc.Crowd(DG)
    return c


def __construct_test_crowd_4nodes_linkedlist():
    # a->b->c->d
    DG = nx.DiGraph()
    DG.add_edge('a','b')
    DG.add_edge('b','c')
    DG.add_edge('c','d')
    c = woc.Crowd(DG)
    return c

def __construct_test_crowd_4nodes_undirected_linklist():
    # a-b-c-d
    UG = nx.Graph()
    UG.add_edge('a','b')
    UG.add_edge('b','c')
    UG.add_edge('c','d')
    uc = woc.Crowd(UG)
    return uc

def __construct_test_crowd_5nodes_shortcut(attrib='T'):
    # a->b->c->d<->e
    # \____________^
    DG = nx.DiGraph()
    DG.add_edge('a','b')
    DG.add_edge('b','c')
    DG.add_edge('c','d')
    DG.add_edge('d','e')
    DG.add_edge('e','d')
    DG.add_edge('a','e')

    if attrib == 'T':
        c = woc.Crowd(DG)
    else:
        c = woc.Crowd(DG,node_key=attrib)
    return c


def __construct_test_crowd_5nodes_withattrib(attrib):
    # Y  N  Y  N   Y
    # a->b->c->d<->e
    # \____________^

    c = __construct_test_crowd_5nodes_shortcut(attrib=attrib)
    nx.set_node_attributes(c.G, {'a': 'yes', 'b': 'no', 'c': 'yes', 'd': 'no', 'e': 'yes'}, name=attrib)
    return c


def __construct_florentine_bidirectional():
    # For a basic statistical analysis of the Florentine network, refer
    # Jackson, M. O. (2010). Social and economic networks. Princeton University Press.
    # Wasserman S. & Faust, K. (1994). Social Network Analysis: Methods and Applications. Cambridge University Press.

    # The networkx generator methodology is discussed in
    # https://networkx.org/documentation/stable/reference/generated/networkx.generators.social.florentine_families_graph.html
    UG = nx.generators.social.florentine_families_graph()
    DG = UG.to_directed()

    # note that networkx's generator does not return the isolated node 'Pucci',
    # which is present in e.g. Jackson (2010) and Wasserman & Faust (1994)...
    # ... to add it manually
    DG.add_node('Pucci')

    # attribute 'T' assigned based on initial letter, either 'a-m' or 'n-z'
    for n in nx.nodes(DG):
        if n[0].lower() >= 'a' and n[0].lower() <= 'm':
            DG.nodes[n]['T'] = 'a-m'
        else:
            DG.nodes[n]['T'] = 'n-z'

    c = woc.Crowd(DG)
    return c


@pytest.mark.filterwarnings("ignore:Performance warning")
def test_is_mk_observer():
    c = __construct_test_crowd_ab_only()
    # cases: invalid m,k-s, missing v's
    with pytest.raises(ValueError):
        c.is_mk_observer('a',-1,-1)
    with pytest.raises(ValueError):
        c.is_mk_observer('a',0,0)
    with pytest.raises(ValueError):
        c.is_mk_observer('a',1,1)
    with pytest.raises(nx.exception.NetworkXError):
        c.is_mk_observer('missing',2,2)

    # cases: since commit on 20211103
    # detect a custom LookupError upon outside modification of graph.
    # decorator @pytest.mark detects and filters the Warning (which is only of use to the human coder)
    with pytest.raises(LookupError):
        c.G.add_edge('x','y')
        c.is_mk_observer('b',2,2)

    # cases: simple 5-nodes as above
    c = __construct_test_crowd_5nodes_shortcut()
    for i in range(1,6,1):
        for j in range(1,6,1): # (k > 1)
            #warnings.warn(str(i) + str(j) + str(c.is_mk_observer('d',i,j)))
            if j==1:
                with pytest.raises(ValueError):
                    c.is_mk_observer('d',i,j)
            elif j==2: # c->d, e->d
                assert c.is_mk_observer('d',i,j) == True
            else:
                assert c.is_mk_observer('d',i,j) == False

    # cases: simple 4-nodes but converted to UNDIRECTED
    c = __construct_test_crowd_4nodes_undirected_linklist()
    for i in range(1,6,1):
        for j in range(1,6,1): # (k > 1)
            if j==1:
                with pytest.raises(ValueError):
                    c.is_mk_observer('c',i,j)
            elif j==2:
                assert c.is_mk_observer('c',i,j) == True
            else:
                assert c.is_mk_observer('c',i,j) == False

    # cases: Florentine graph, considering node=Medici
    c = __construct_florentine_bidirectional()
    # NB: loops intentionally unrolled to clearly demonstrate ground truth
    # m/k   1    2    3    4    5
    # ------------------------------
    # 1     Err  Y    Y    Y    Y
    # 2     Err  Y    Y    Y    Y
    # 3     Err  Y    Y    Y    Y
    # 4     Err  Y    Y    Y    N
    # 5     Err  Y    Y    Y    N
    # ------------------------------
    k = 1
    for m in [1,2,3,4,5]: # k=1 is undefined
        with pytest.raises(ValueError):
            c.is_mk_observer('Medici', m, k)

    k = 2
    for m in [1,2,3,4,5]: # at least 2 observers m=[1..5] apart
        assert c.is_mk_observer('Medici', m, k) == True # Accaiuoli-Salviati infinitely apart

    k = 3
    for m in [1,2,3,4,5]: # at least 3 observers...
        assert c.is_mk_observer('Medici', m, k) == True # Accaiuoli-Salviati infinitely apart from Barbadori

    k = 4
    for m in [1,2,3,4,5]: # at least 4 observers...
        assert c.is_mk_observer('Medici', m, k) == True # Accaiuoli-Salviati inf, Barbadori-Tornabuoni (OR Barbadori-Albizzi): 4 nodes, >4-independent (via Castellani...)

    k = 5
    for m in [1,2,3]: # at least k=5 observers...
        assert c.is_mk_observer('Medici', m, k) == True # Accaiuoli-Salviati inf, Barbadori-Ridolfi, Barbadori-Albizzi: 5 nodes, <=3-independent (cannot consider Tornabuoni shortcut)
    for m in [4,5]:
        assert c.is_mk_observer('Medici', m, k) == False # ...as above, can't find any 5 nodes w/4-deg-of-separation minimum


def test_S():
    c = __construct_test_crowd_ab_only()
    # case: missing v's
    with pytest.raises(nx.exception.NetworkXError):
        c.S('missing')

    # case: simple 5-nodes as above
    c = __construct_test_crowd_5nodes_shortcut()
    assert c.S('d') == 5*2 # largest combo c.is_mk_observer('d',5,2)

    # case: Florentine graph, considering node=Medici
    c = __construct_florentine_bidirectional()
    assert c.S('Medici') == 5*4 # largest combo c.is_mk_observer('Medici', 5, 4)


def test_D():
    c = __construct_test_crowd_ab_only()
    # cases: missing v's
    with pytest.raises(nx.exception.NetworkXError):
        c.D('missing')

    # case: no such attrib, given default node_key = 'T'
    assert c.D('a') == 0

    # case: using default node_key = 'T'
    c = __construct_test_crowd_5nodes_withattrib('T')
    assert c.D('e') == 2  # d=N, a=Y, topics=len(YN)=2
    assert c.D('a') == 0
    assert c.D('b') == 1

    c = __construct_test_crowd_5nodes_withattrib('sentiment')
    assert c.D('e') == 2  # d=N, a=Y, topics=len(YN)=2
    assert c.D('a') == 0
    assert c.D('b') == 1

    # cases: Florentine graph, considering node=Medici, default node_key = 'T'
    c = __construct_florentine_bidirectional()
    assert c.D('Medici') == 2  # connected with e.g. Ridolfi ('n-z'), Albizzi ('a-m'), hence topics = len(['a-m','n-z']) = 2
    assert c.D('Pucci')  == 0  # not connected with anything
    assert c.D('Lamberteschi') == 1 # only connected with Guadagni ('a-m')
    assert c.D('Pazzi') == 1 # only connected with Salviati ('n-z')


def test_pi():
    c = __construct_test_crowd_ab_only()
    # case: missing v's
    with pytest.raises(nx.exception.NetworkXError):
        c.pi('missing')

    # case: using default node_key = 'T'
    c = __construct_test_crowd_5nodes_withattrib('T')
    assert c.pi('e') == c.S('e')*c.D('e') == 6*2

    # case: Florentine graph, considering node=Medici, default node_key = 'T'
    c = __construct_florentine_bidirectional()
    assert c.pi('Medici') == c.S('Medici')*c.D('Medici') == 20*2


def test_h_measure():
    c = __construct_test_crowd_ab_only()
    # case: missing v's
    with pytest.raises(nx.exception.NetworkXError):
        c.S('missing')

    # case: simple 5-nodes as above
    c = __construct_test_crowd_5nodes_shortcut()
    assert c.h_measure('d') == 2 # i = 2 === k = 2 max (per is_mk_observer)

    # cases simple 5-nodes as above, constrained h=k=2
    c = __construct_test_crowd_5nodes_shortcut()
    assert c.h_measure('d', max_h=2) == 2 # i = 1 === k = 1 max (per is_mk_observer)

    # case: Florentine graph, considering node=Medici
    c = __construct_florentine_bidirectional()
    assert c.h_measure('Medici') == 4


@pytest.mark.filterwarnings("ignore:Performance warning")
def test_clear_path_dict():
    c = __construct_test_crowd_ab_only()

    c.G.add_edge('x','y')
    # precondition: since commit on 20211103
    # firstly, detect a custom LookupError upon outside modification of graph.
    # decorator @pytest.mark detects and filters the Warning (which is only of use to the human coder)
    assert c.refresh_requested == False
    with pytest.raises(LookupError):
        c.is_mk_observer('b',2,2)

    # case: ensure clear_path_dict does its job...
    c.clear_path_dict()
    assert c.precomputed_path_dict == {}
    assert len(c.precomputed_paths_by_hole_node) == 0
    assert c.s_cache == {}
    assert c.refresh_requested == True
    c.is_mk_observer('b',2,2) # this should NOT trigger an error
    assert c.refresh_requested == False

    # ... if we repeat everything above, starting from tampering with the graph,
    # this should now re-trigger an error, get fixed by the user's clear_path_dict, and be back to normal
    c.G.add_edge('xx','yy')
    assert c.refresh_requested == False
    with pytest.raises(LookupError):
        c.is_mk_observer('b',2,2)
    c.clear_path_dict()
    assert c.precomputed_path_dict == {}
    assert len(c.precomputed_paths_by_hole_node) == 0
    assert c.s_cache == {}
    assert c.refresh_requested == True
    c.is_mk_observer('b',2,2) # this should NOT trigger an error
    assert c.refresh_requested == False


# mock patch for pyplot.show - we don't want the plot window to pop up every time
from unittest.mock import patch
@patch('matplotlib.pyplot.show')
def test_make_sullivanplot(mock_show):
    # case: pass lists of imbalanced-length [pis, Ds, Ses]
    with pytest.raises(AssertionError):
        woc.make_sullivanplot([1,2],[1],[1])
    with pytest.raises(AssertionError):
        woc.make_sullivanplot([1],[1,2],[1])
    with pytest.raises(AssertionError):
        woc.make_sullivanplot([1],[1],[1,2])

    # case: pass lists of 0-length
    with pytest.raises(AssertionError):
        woc.make_sullivanplot([],[],[])

    # case: pass basic and optional params for standard runs; should return None successfully
    assert woc.make_sullivanplot([1,2,3,4,5],[1,2,3,4,5],[1,2,3,4,5]) == None
    assert woc.make_sullivanplot([1,2,3,4,5],[1,2,3,4,5],[1,2,3,4,5], suptitle="Test") == None
    assert woc.make_sullivanplot([1,2,3,4,5],[1,2,3,4,5],[1,2,3,4,5], colormap = 'Spectral') == None
    assert woc.make_sullivanplot([1,2,3,4,5],[1,2,3,4,5],[1,2,3,4,5], cax = matplotlib.pyplot.axes()) == None
    assert woc.make_sullivanplot([1,2,3,4,5],[1,2,3,4,5],[1,2,3,4,5], yscale="linear") == None


def test_iteratively_prune_graph():
    # case: pass a Crowd instead
    with pytest.raises(TypeError):
        woc.iteratively_prune_graph(__construct_florentine_bidirectional())

    # case: standard graph for Florentine, threshold=1
    # first pass removes Pucci, Lamberteschi, Ginori, Acciaiuoli, Pazzi;
    # second pass removes Salviati
    H = nx.generators.social.florentine_families_graph()
    G = woc.iteratively_prune_graph(H)
    for existing in ['Albizzi', 'Guadagni', 'Bischeri', 'Peruzzi', 'Castellani', \
                    'Barbadori', 'Medici', 'Tornabuoni', 'Ridolfi', 'Strozzi']:
        assert existing in G.nodes
    for removed in ['Pucci', 'Lamberteschi', 'Ginori', 'Acciaiuoli', 'Salviati', 'Pazzi']:
        assert removed not in G.nodes

    # case: DIgraph for Florentine, threshold=1
    # should have everything intact, except the isolated Pucci
    # as the digraph effectively doubles the degree (--- = --> + <--) per node
    DH = H.to_directed()
    DG = woc.iteratively_prune_graph(DH)
    for existing in ['Albizzi', 'Guadagni', 'Bischeri', 'Peruzzi', 'Castellani', \
                    'Barbadori', 'Medici', 'Tornabuoni', 'Ridolfi', 'Strozzi',
                    'Lamberteschi', 'Ginori', 'Acciaiuoli', 'Salviati', 'Pazzi']:
        assert existing in DG.nodes
    for removed in ['Pucci']:
        assert removed not in DG.nodes

    # case: standard graph for Florentine, with threshold=2; should be a null graph
    G = woc.iteratively_prune_graph(H, threshold=2)
    assert len(G.edges) == len(G.nodes) == 0

    # case: pass a graph without edgeweights despite specifying so.
    with pytest.raises(KeyError):
        G = woc.iteratively_prune_graph(H, weight_threshold=2, weight_key='no-such-key')

    # case: standard graph for Florentine, threshold=1; with
    # edge culling threshold=2 - only one triangle should remain (with edgeweights=100)
    H = nx.generators.social.florentine_families_graph()
    nx.set_edge_attributes(H, 1, 'edgeweight')
    H.edges['Medici','Ridolfi']['edgeweight'] = 100
    H.edges['Medici','Tornabuoni']['edgeweight'] = 100
    H.edges['Ridolfi','Tornabuoni']['edgeweight'] = 100
    G = woc.iteratively_prune_graph(H, weight_threshold=2, weight_key='edgeweight')
    for existing in ['Ridolfi', 'Medici', 'Tornabuoni']:
        assert existing in G.nodes
    for removed in ['Guadagni', 'Bischeri', 'Peruzzi', 'Castellani', 'Barbadori', \
                    'Albizzi', 'Strozzi', 'Lamberteschi', 'Ginori', 'Acciaiuoli', \
                    'Salviati', 'Pazzi', 'Pucci']:
        assert removed not in G.nodes
