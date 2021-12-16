# wisdom-of-crowds

### The package

This package provides a replication and extension of the measures described in Sullivan et al. (2020) Vulnerability in Social Epistemic Networks *International Journal of Philosophical Studies*  https://doi.org/10.1080/09672559.2020.1782562


The core idea is that we can get a sense of the epistemic position of people in a social network--conceived of as a directed graph--by looking at both the diversity and relatedness of their sources. The key concept is that of an m,k-observer: a node n is an m,k-observer just in case it has at least one set of m source nodes that are pairwise at least k-distant from one another along paths that do not include n. Distance is assumed to be directed, though the measure is defined for undirected graphs.

The package itself provides a single class ``Crowd()`` which is initialized with a ``networkx`` graph (typically a ``DiGraph``).

``Crowd()`` allows for computation of several functions directly. Most functions call ``is_mk_observer(node,m,k)`` The function ``S(node)`` gives the max m\*k for which  node is an m,k-observer. The function ``h_measure(node)`` returns the max h such that node is an h,h-observer (compare to the h-index).

There is also a function ``D(node)`` that returns the *diversity* of a node, defined as the number of distinct  sources from which a node receives testimony. This requires an  attribute (default `'T'`) which is used to query either inbound nodes or edges (edges not yet implemented). The attribute may yield a single value or a set of values.  ``D(node)`` is defined as the number of distinct values  across all source nodes/edges.  Finally, ``pi(node)`` is defined as D*S.

By convention, a node with a single input is an 1,1-observer. As per Sullivan et al, ``S`` is not calculated for k<2, so a node with a single input or one input has S=0.

### Implementation notes

Determining whether a node is an m,k-observer involves solving combinatorially many multiple shortest path problems along with a minimal independent set problem. Both are computationally demanding. Our goal was to be able to run the above algorithms on large graphs in a reasonable time.

To that end, there are several speedups implemented. Behind the scenes ``Crowd`` does a lot of caching of seen paths. The means that lookups for single nodes may seem slow, but iterating over all nodes ofen speeds up over time. It also means that pickling a ``Crowd()`` can result in surprisingly large files, though on the plus side it means that re-computing values is often trivial.  The clique-finding problem is optimized to terminate early if possible, but verifying that a node is *not* an m,k-observer can be time consuming on nodes with a large number of sources.

On the plus side, the optimizations mean that calcluating measures for an entire graph can be very fast. It is possible to compute (e.g.) measures for every node in a realistic social graph (tens of thousands of nodes,  hundreds of thousands of edges) a few hours on desktop machines.
