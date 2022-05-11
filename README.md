# wisdom-of-crowds

![coverage](https://raw.githubusercontent.com/cvklein/wisdom-of-crowds/main/tests/.reports/coverage-badge.svg)
![tests](https://raw.githubusercontent.com/cvklein/wisdom-of-crowds/main/tests/.reports/tests-badge.svg)
![shields.io-issues](https://img.shields.io/github/issues/cvklein/wisdom-of-crowds)
![shields.io-forks](https://img.shields.io/github/forks/cvklein/wisdom-of-crowds)
![shields.io-stars](https://img.shields.io/github/stars/cvklein/wisdom-of-crowds)
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

### The package

This package provides a replication and extension of the measures described in Sullivan et al. (2020) Vulnerability in Social Epistemic Networks *International Journal of Philosophical Studies*  https://doi.org/10.1080/09672559.2020.1782562


The core idea is that we can get a sense of the epistemic position of people in a social network--conceived of as a directed graph--by looking at both the diversity and relatedness of their sources. The key concept is that of an m,k-observer: a node n is an m,k-observer just in case it has at least one set of m source nodes that are pairwise at least k-distant from one another along paths that do not include n. Distance is assumed to be directed, though the measure is defined for undirected graphs.

The package itself provides a single class ``Crowd()`` which is initialized with a ``networkx`` graph (typically a ``DiGraph``).

``Crowd()`` allows for computation of several functions directly. Most functions call ``is_mk_observer(node,m,k)`` The function ``S(node)`` gives the max m\*k for which  node is an m,k-observer. The function ``h_measure(node)`` returns the max h such that node is an h,h-observer (compare to the h-index).

There is also a function ``D(node)`` that returns the *diversity* of a node, defined as the number of distinct  sources from which a node receives testimony. This requires an  attribute (default `'T'`) which is used to query inbound nodes. The attribute may yield a single value or a set of values.  ``D(node)`` is defined as the number of distinct values  across all source nodes/edges.  Finally, ``pi(node)`` is defined as D*S.

As per Sullivan et al, ``S`` is not calculated for k<2, so a node with zero or one inputs has S=0.

### Quick start guide
For example, given a ``networkx`` graph, say a digraph ``G`` of a social network, we can easily use the package as follows:
```python
c = Crowd(G)            # defaults

check_n = c.is_mk_observer('n',3,3) # checks if node 'n' in G is a 3,3-observer
S_n = c.S('n')          # returns the S-value of node 'n'; S = max_{(m,k) in MK}(m * k)
D_n = c.D('n')          # returns the D-value (Diversity) of node 'n'
pi_n = c.pi('n')        # returns the pi-value of node 'n'; pi = S * D
h_n = c.h_measure('n')  # returns the h-measure of node 'n'; the highest h for which mk_observer('n', h, h) is True
```

### Example with visualization
Refer to [``example notebook.ipynb``](https://github.com/cvklein/wisdom-of-crowds/blob/main/example%20notebook.ipynb) for a more detailed ready-to-use example with visualization.

### Documentation
The documentation is available [here](https://github.com/cvklein/wisdom-of-crowds/blob/main/docs/wisdom_of_crowds.py.md), generated using the amazing ``lazydocs`` tool.

### Implementation notes

Determining whether a node is an m,k-observer involves solving combinatorially many multiple shortest path problems along with a minimal independent set problem. Both are computationally demanding. Our goal was to be able to run the above algorithms on large graphs in a reasonable time.

To that end, there are several speedups implemented. Behind the scenes ``Crowd`` does a lot of caching of seen paths. The means that lookups for single nodes may seem slow, but iterating over all nodes ofen speeds up over time. It also means that pickling a ``Crowd()`` can result in surprisingly large files, though on the plus side it means that re-computing values is often trivial.  The clique-finding problem is optimized to terminate early if possible, but verifying that a node is *not* an m,k-observer can be time consuming on nodes with a large number of sources.

On the plus side, the optimizations mean that calcluating measures for an entire graph can be very fast. It is possible to compute (e.g.) measures for every node in a realistic social graph (tens of thousands of nodes,  hundreds of thousands of edges) in a few hours on desktop machines.


### License and Citation

This software is released under the GNU General Public License version 3 (GPL3.0) [https://opensource.org/licenses/GPL-3.0](https://opensource.org/licenses/GPL-3.0)

If you use this package, we'd appreciate a citation! (Watch this space for details)

### Version history

v1.01 2 Mar 2022 -- License update

v1.0  17 Dec 2021  -- released to public


#### Technologies and components used
* Libraries: ``networkx``, ``matplotlib``, ``pytest``, ``coverage``
* Documentation/badging: ``lazydocs``, ``genbadge``, *shields.io*
