<!-- markdownlint-disable -->

<a href="../wisdom_of_crowds.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `wisdom_of_crowds.py`





---

<a href="../wisdom_of_crowds.py#L375"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

* One, you can just pass a list of pis, Ds, and Ses, optionally with a colormap and a suptitle.  This will make and render a plot  

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

<a href="../wisdom_of_crowds.py#L490"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `iteratively_prune_graph`

```python
iteratively_prune_graph(
    H,
    threshold=1,
    weight_threshold=None,
    weight_key='weight',
    verbose=False
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

<a href="../wisdom_of_crowds.py#L33"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `__init__`

```python
__init__(G, max_m=5, node_key='T')
```

Constructor:  `__init__`: Inits the Crowd object. 



**Args:**
 
 - <b>`G`</b>:  a networkx graph, typically DiGraph. 
 - <b>`max_m`</b>:  maximum m to consider in the calculations 
 - <b>`node_key`</b>:  attribute to consider for each node, when considering topic diversity (defaults to 'T') 




---

<a href="../wisdom_of_crowds.py#L301"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `D`

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

<a href="../wisdom_of_crowds.py#L264"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `S`

```python
S(v)
```

S: calculates S, defined in (Sullivan et al., 2020) as the structural position of v.  

 S = max_{(m,k) in MK}(m * k)  



**Args:**
 
 - <b>`v`</b>:  vertex to evaluate 



**Returns:**
 integer S, in range 0 <= (class constant max_m * class constant max_k) 

---

<a href="../wisdom_of_crowds.py#L356"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `clear_path_dict`

```python
clear_path_dict()
```

clear_path_dict: helper function to completely reset the precomputed path dictionary. Should be used if G is changed. 

---

<a href="../wisdom_of_crowds.py#L340"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `h_measure`

```python
h_measure(v, max_h=6)
```

h_measure: find the highest h, given vertex v, of which mk_observer(v, h, h) is true 



**Args:**
 
 - <b>`v`</b>:  vertex to evaluate 
 - <b>`max_h`</b>:  maximum_h to evaluate, defaults to 6 per (Sullivan et al., 2020) 



**Returns:**
 integer h, in range 1 < h <= max_h 

---

<a href="../wisdom_of_crowds.py#L163"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `is_mk_observer`

```python
is_mk_observer(v, m, k)
```

is_mk_observer: checks if the vertex v is an (m,k)-observer as defined by (Sullivan et al., 2020);  optimized clique-finding algo by CVK. 



**Args:**
 
 - <b>`v`</b>:  vertex to evaluate 
 - <b>`m`</b>:  m as defined in (Sullivan et al., 2020); m >= 1 
 - <b>`k`</b>:  k as defined in (Sullivan et al., 2020); k > 1 



**Returns:**
 a boolean indicating the m,k-observer status of v 

---

<a href="../wisdom_of_crowds.py#L327"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `pi`

```python
pi(v)
```

pi: calculates pi, given vertex v, defined in (Sullivan et al., 2020) as the product of S and D 



**Args:**
 
 - <b>`v`</b>:  vertex to evaluate 



**Returns:**
 integer pi, where pi = S * D 

---

<a href="../wisdom_of_crowds.py#L140"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `shortest_path_length_node_source_target`

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
