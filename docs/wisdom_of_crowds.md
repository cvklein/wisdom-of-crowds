<!-- markdownlint-disable -->

<a href="../src/wisdom_of_crowds.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `wisdom_of_crowds`





---

<a href="../src/wisdom_of_crowds.py#L523"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `make_sullivanplot`

```python
make_sullivanplot(
    pis,
    ds,
    ses,
    colormap='gist_yarg',
    suptitle=None,
    cax=None,
    yscale='linear'
)
```

make_sullivanplot: This makes the style of plot from Sullivan et al (2020). 

cvk note: Could be more generic, but essentially has two modes:  

* One, you can just pass a list of pis, Ds, and Ses, optionally with a colormap and a subtitle.  This will make and render a plot  

* Two, or else you can pass an axis (and optionally colormap and suptitle)  and this will render it on the axis, allowing for multiple plots (as done in the paper figures). 



**Args:**
 
 - <b>`pis`</b>:  a list of pi-s 
 - <b>`ds`</b>:   a list of D-s 
 - <b>`ses`</b>:  a list of S-s 
 - <b>`colormap`</b>:  (optional) name of a colormap, defaults to 'gist_yarg' 
 - <b>`suptitle`</b>:  (optional) supplementary title 
 - <b>`cax`</b>:   (optional) axis to render on 
 - <b>`yscale`</b>:  (optional) scale of y-axis. Defaults to linear. 

Precondition: 
 - <b>`PRECONDITION`</b>:  len(pis) == len(Ds) == len(Ses) == X, where len(X) > 0 



**Returns:**
 None on success; but generates the plot in a plt window. 


---

<a href="../src/wisdom_of_crowds.py#L638"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `iteratively_prune_graph`

```python
iteratively_prune_graph(
    H,
    threshold=1,
    weight_threshold=None,
    weight_key='weight'
)
```

iteratively_prune_graph: Iterative graph pruner, provided as a helper function. 

With no arguments, it iteratively prunes as per Sullivan et al (2020). i.e. culls all nodes with indegree + outdegree <= 1, takes the largest connected component, and iterates until stable. It also adds the possibility of a weight threshold, which is useful for bigger/denser graphs. cvk note: I ended up making a copy b/c in-place destructive changes are easier than playing with subgraphs 



**Args:**
 
 - <b>`H`</b>:  source graph - will not be modified. [NB: this is nx.Graph; NOT Crowd. An assertion will test for this.] 
 - <b>`threshold`</b>:  (optional) threshold T where indegree+outdegree <= T 
 - <b>`weight_threshold`</b>:  (optional) allows specification of weights-per-edge. This throws an exception if edges are not weighted 
 - <b>`weight_key`</b>:  (optional) identifies key used for weight thresholding. Ignored if weight_threshold is not specified. 
 - <b>`verbose`</b>:  (optional) debugging flag for verbose reporting 



**Returns:**
 
 - <b>`G`</b>:  pruned graph, which is a full (deep) copy of H then pruned. 


---

<a href="../src/wisdom_of_crowds.py#L13"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Crowd`
Class for encapsulating a graph and pre-computed (memoized) features for the Wisdom of Crowds algorithm, per Sullivan et al. (2020), 

"Vulnerability in Social Epistemic Networks" *International Journal of Philosophical Studies* https://doi.org/10.1080/09672559.2020.1782562 



**Attributes:**
 
 - <b>`G`</b>:  networkx graph (see __init__) 
 - <b>`min_k`</b>:  smallest k to consider during processing, defaults to 2 
 - <b>`max_k`</b>:  largest k to consider during processing, defaults to 5 
 - <b>`min_m`</b>:  smallest m to consider during processing, defaults to 1 
 - <b>`max_m`</b>:  largest m to consider during processing 
 - <b>`node_key`</b>:  attribute to consider for each node (see __init__)         
 - <b>`precomputed_path_dict`</b>:  cache for unconditional paths 
 - <b>`precomputed_paths_by_hole_node`</b>:  cache for dict of paths per node 
 - <b>`refresh_requested`</b>:  flag indicating if cache has expired 
 - <b>`node_set`</b>:  a snapshot of nodes to detect cache expiry 
 - <b>`edge_set`</b>:  a snapshot of nodes to detect cache expiry 
 - <b>`s_cache`</b>:  cached versions of S results 

<a href="../src/wisdom_of_crowds.py#L35"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(G, max_m=5, node_key='T')
```

Constructor:  `__init__`: Inits the Crowd object. 



**Args:**
 
 - <b>`G`</b>:  a networkx graph, typically DiGraph. 
 - <b>`max_m`</b>:  maximum m to consider in the calculations 
 - <b>`node_key`</b>:  attribute to consider for each node, when considering topic diversity (defaults to 'T') 




---

<a href="../src/wisdom_of_crowds.py#L410"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `D`

```python
D(v)
```

D: calculates D, defined in the literature as the number of topics found for  informants of vertex v per (Sullivan et al., 2020)  

 We apply the general case D = D' = | union_{(u,v) in E} C'(u) |  



**Args:**
 
 - <b>`v`</b>:  vertex to evaluate 



**Returns:**
 integer D, in range 0 <= D 

---

<a href="../src/wisdom_of_crowds.py#L372"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `D_edge`

```python
D_edge(v, depth=None, selection=None)
```

D_edge: calculates D edge-wise by seeing which topics are transmitted by the   informants of vertex v per (Sullivan et al. 2020) 



**Args:**
 
 - <b>`v            `</b>:  vertex to evaluate 
 - <b>`depth        `</b>:  if we want to look past the immediate soures, how far back to look 
 - <b>`selection    `</b>:  if we want to only look at a selection of sources, these are the ones 



**Returns:**
 integer D_edge, in range 0 <= total topics attested in graph 

---

<a href="../src/wisdom_of_crowds.py#L284"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `S`

```python
S(v, show_mk=False, transmit=False)
```

S: calculates S, defined in (Sullivan et al., 2020) as the structural position of v.  If transmit == True, instead calculates calculates T, the inverse of S, i.e. the structural position of v as a transmitter. If mk == True, instead returns a tuple (S, m, k). To speed up future calculations, it also caches the result (S, (m, k)) in the s_cache dictionary. 

 S = max_{(m,k) in MK}(m * k)  T = max_{(m,k) in MK}(m * k), but running is_m_k_observer() with transmit = True  



**Args:**
 
 - <b>`v`</b>:           vertex to evaluate 
 - <b>`show_mk`</b>:     whether to return the m,k values along with S 
 - <b>`transmit`</b>:    whether to calculate the position as transmitter 



**Returns:**
 integer S or T, in range 0 <= (class constant max_m * class constant max_k) or tuple (S, (m, k)) 

---

<a href="../src/wisdom_of_crowds.py#L474"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `census`

```python
census(nbunch=None, topics=False)
```

census: outputs a data structure containing the WoC network centrality measures for the nodes in the network (by default, all the nodes). Can be specified to also include the values about the topics the node transmits and receives about.  



**Args:**
 
 - <b>`nbunch`</b>:  if specified, will only return the values for these nodes, takes a list, set, graph, etc. 
 - <b>`topics`</b>:  Boolean which, if True, makes the function also output the measures about topics (D, pi, pi_t). 



**Returns:**
 dict output, with dictionaries of the WoC values keyed by node 

---

<a href="../src/wisdom_of_crowds.py#L504"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `clear_path_dict`

```python
clear_path_dict()
```

clear_path_dict: helper function to completely reset the precomputed path dictionary. Should be used if G is changed. 

---

<a href="../src/wisdom_of_crowds.py#L349"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `count_topics`

```python
count_topics(v)
```

count_topics: return the number of distinct topics transmitted by vertex v, topics should be in a set if multiple 



**Args:**
 
 - <b>`v`</b>:           vertex to evaluate         

**Returns:**
 integer counter 

---

<a href="../src/wisdom_of_crowds.py#L451"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `h_measure`

```python
h_measure(v, max_h=6, transmit=False)
```

h_measure: find the highest h, given vertex v, of which mk_observer(v, h, h) is true 



**Args:**
 
 - <b>`v`</b>:           vertex to evaluate 
 - <b>`max_h`</b>:       maximum_h to evaluate, defaults to 6 per (Sullivan et al., 2020) 
 - <b>`transmit`</b>:    whether to calculate the position as transmitter 



**Returns:**
 integer h, in range 1 < h <= max_h 

---

<a href="../src/wisdom_of_crowds.py#L174"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `is_mk_observer`

```python
is_mk_observer(v, m, k, transmit=False)
```

is_mk_observer: checks if the vertex v is an (m,k)-observer as defined by (Sullivan et al., 2020);  optimized clique-finding algo by CVK. 

If transmit=True, runs the algorithm but checks the node's position as a transmitter. This has the same result as running the algorithm on the reverse of the graph,   but is much more efficient due to not having redo the calculations for the reversed graph. 



**Args:**
 
 - <b>`v       `</b>:  vertex to evaluate 
 - <b>`m       `</b>:  m as defined in (Sullivan et al., 2020); m >= 1 
 - <b>`k       `</b>:  k as defined in (Sullivan et al., 2020); k > 1 
 - <b>`transmit`</b>:  boolean (defaults False) 



**Returns:**
 a boolean indicating the m,k-observer status of v 

---

<a href="../src/wisdom_of_crowds.py#L435"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `pi`

```python
pi(v, transmit=False)
```

pi: calculates pi, given vertex v, defined in (Sullivan et al., 2020) as the product of S and D for observers,  for transmitters it calculates pi_t as the product of St and the amount of topics it transmits itself. 



**Args:**
 
 - <b>`v`</b>:  vertex to evaluate 



**Returns:**
 integer pi, where pi = S * D 

---

<a href="../src/wisdom_of_crowds.py#L151"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `shortest_path_length_node_source_target`

```python
shortest_path_length_node_source_target(v, source, target)
```

shortest_path_length_node_source_target: wrapper function to get the length of the  shortest path between vertices source and target, without vertex v.  

 no path = infinite length  



**Args:**
 
 - <b>`v`</b>:  vertex under consideration, as defined by (Sullivan et al., 2020) 
 - <b>`source`</b>:  source node 
 - <b>`target`</b>:  target node 



**Returns:**
 integer z, in range 0 <= z <= +infinity 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
