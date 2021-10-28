import pytest
import warnings
import networkx as nx
import wisdom_of_crowds as woc


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
    c = __construct_test_crowd_ab_only()
    with pytest.warns(Warning, match='Performance warning'):
        c.G.add_edge('x','y')
        c._Crowd__shortest_path_node_source_target('b','x','y')
    
    # case: no such node(s), expect nx.NodeNotFound to be raised by either Crowd or Graph
    c = __construct_test_crowd_ab_only()
    with pytest.raises(nx.NodeNotFound):
        c._Crowd__shortest_path_node_source_target('missing','a','b')
    with pytest.raises(nx.NodeNotFound):
        c._Crowd__shortest_path_node_source_target('a','missing','b')
    with pytest.raises(nx.NodeNotFound):
        c._Crowd__shortest_path_node_source_target('a','b','missing')

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
    c = __construct_test_crowd_ab_only()
    with pytest.warns(Warning, match='Performance warning'):
        c.G.add_edge('x','y')
        c.shortest_path_length_node_source_target('b','x','y')

    # case: no such node(s), expect nx.NodeNotFound to be raised by either Crowd or Graph
    c = __construct_test_crowd_ab_only()
    with pytest.raises(nx.NodeNotFound):
        c.shortest_path_length_node_source_target('missing','a','b')
    with pytest.raises(nx.NodeNotFound):
        c.shortest_path_length_node_source_target('a','missing','b')
    with pytest.raises(nx.NodeNotFound):
        c.shortest_path_length_node_source_target('a','b','missing')

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


def test_is_mk_observer():
    c = __construct_test_crowd_ab_only()
    # cases: invalid m,k-s, missing v's
    with pytest.raises(ValueError):
        c.is_mk_observer('a',-1,-1) 
    with pytest.raises(ValueError):
        c.is_mk_observer('a',0,0) 
    with pytest.raises(nx.exception.NetworkXError):
        c.is_mk_observer('missing',1,1)

    # cases: simple 5-nodes as above
    c = __construct_test_crowd_5nodes_shortcut()  
    for i in range(1,6,1):
        for j in range(1,6,1):
            #warnings.warn(str(i) + str(j) + str(c.is_mk_observer('d',i,j)))
            if j==1 or j==2: # c->d, e->d
                assert c.is_mk_observer('d',i,j) == True
            else:
                assert c.is_mk_observer('d',i,j) == False


def test_S():
    c = __construct_test_crowd_ab_only()
    # cases: missing v's
    with pytest.raises(nx.exception.NetworkXError):
        c.S('missing')

    # cases: simple 5-nodes as above
    c = __construct_test_crowd_5nodes_shortcut()  
    assert c.S('d') == 10 # i = 5 (runs out), k = 2 max (per is_mk_observer)


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


def test_pi():
    c = __construct_test_crowd_ab_only()
    # cases: missing v's
    with pytest.raises(nx.exception.NetworkXError):
        c.pi('missing')

    # case: using default node_key = 'T'
    c = __construct_test_crowd_5nodes_withattrib('T')
    assert c.pi('e') == c.S('e')*c.D('e')

def test_h_measure():
    c = __construct_test_crowd_ab_only()
    # cases: missing v's
    with pytest.raises(nx.exception.NetworkXError):
        c.S('missing')

    # cases: simple 5-nodes as above
    c = __construct_test_crowd_5nodes_shortcut()  
    assert c.h_measure('d') == 2 # i = 2 === k = 2 max (per is_mk_observer)

    # cases: simple 5-nodes as above, constrained h=k=1
    c = __construct_test_crowd_5nodes_shortcut()  
    assert c.h_measure('d', max_h=1) == 1 # i = 1 === k = 1 max (per is_mk_observer)
