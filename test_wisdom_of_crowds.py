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

    # cases: Florentine graph, considering node=Medici
    c = __construct_florentine_bidirectional()
    for m in [1,2,3,4,5]: # at least 1 observer  m=[1..5] apart
        assert c.is_mk_observer('Medici', m, 1) == True # trivial case of Accaiuoli

    for m in [1,2,3,4,5]: # at least 2 observers m=[1..5] apart
        assert c.is_mk_observer('Medici', m, 2) == True # Accaiuoli-Salviati infinitely apart

    for m in [1,2,3,4,5]: # at least 3 observers...
        assert c.is_mk_observer('Medici', m, 3) == True # Accaiuoli-Salviati infinitely apart from Barbadori

    for m in [1,2,3,4,5]: # at least 4 observers...
        assert c.is_mk_observer('Medici', m, 4) == True # Accaiuoli-Salviati inf, Barbadori-Tornabuoni (OR Barbadori-Albizzi): 4 nodes, >4-independent (via Castellani...)

    for m in [1,2,3,4,5]: # at least k=5 observers...
        if m <= 3:
            assert c.is_mk_observer('Medici', m, 5) == True # Accaiuoli-Salviati inf, Barbadori-Ridolfi, Barbadori-Albizzi: 5 nodes, <=3-independent (cannot consider Tornabuoni shortcut)
        else:
            assert c.is_mk_observer('Medici', m, 5) == False # ...as above, can't find any 5 nodes w/4-deg-of-separation minimum

    for m in [1,2,3,4,5]: # at least k=6 observers...
        if m == 1:
            assert c.is_mk_observer('Medici', m, 6) == True # Accaiuoli-Salviati inf, Barbadori/Ridolfi/Tornabuoni/Albizzi at most 1-independent (Ridolfi neighbours Tornabuoni)
        else:
            assert c.is_mk_observer('Medici', m, 6) == False # ...as above, can't find any combinations of nodes w/ 6-deg-of-separation minimum


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

    # cases simple 5-nodes as above, constrained h=k=1
    c = __construct_test_crowd_5nodes_shortcut()  
    assert c.h_measure('d', max_h=1) == 1 # i = 1 === k = 1 max (per is_mk_observer)

    # case: Florentine graph, considering node=Medici
    c = __construct_florentine_bidirectional()
    assert c.h_measure('Medici') == 4