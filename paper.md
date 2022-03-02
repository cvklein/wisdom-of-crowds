---
title: '`wisdom_of_crowds`: A Python package for social-epistemological network profiling'
tags:
  - Python
  - epistemic networks
  - social epistemology
  - network epistemology
  - testimony
authors:
  - name: Colin Klein^[co-first author] ^[corresponding author] # note this makes a footnote saying 'co-first author'
    orcid: 0000-0002-7406-4010
    affiliation: 1 # (Multiple affiliations must be quoted)
  - name: Marc Cheong^[co-first author] # note this makes a footnote saying 'co-first author'
    orcid: 0000-0002-0637-3436
    affiliation: 2
  - name: Marinus Ferreira
    orcid: 0000-0002-3571-9221
    affiliation: 3
  - name: Emily Sullivan
    orcid: 0000-0002-2073-5384
    affiliation: 4
  - name: Mark Alfano
    orcid: 0000-0001-5879-8033
    affiliation: 3
affiliations:
 - name: The Australian National University
   index: 1
 - name: University of Melbourne
   index: 2
 - name: Macquarie University
   index: 3
 - name: Eindhoven University
   index: 4
date: 2 Mar 2022
bibliography: paper.bib

---

# Summary

Most of what we know we know because we learned about it from other people. \emph{Social epistemology} is the subfield of philosophy that studies how knowledge and justification depend on the testimony of others [@goldman1999knowledge]. In recent years, social epistemologists have moved away from considering dyadic relationships between individuals to consider the ways in which social epistemic \emph{networks} shape the information we receive [@o2019misinformation; @alfano2020humility]. A focus on networks has been influential because it allows philosophers to connect their concerns to the substantial body of empirical and simulation work on real-world networks and their graph-theoretic properties.

 Broadly speaking, individuals are in a better epistemic position if they are receiving information from diverse and independent sources, with the more diversity and independence the better.  Sullivan et al. quantified this relationship by introducing the idea of an $m,k$-observer. Given a graph $G$, say that a node $n$ is an $m,k$-observer just in case it receives information from a set of at least $k$ different nodes which are pairwise at least $m$ steps away from one another, when considered on the subgraph of $G$ that does not contain $n$. If $G$ is directed, then candidate sources must be at least $m$ steps away in both directions. The present package provides an efficient method to calculate this measure (and other derived concepts) on arbitrary graphs.



# Statement of need

[@SullivanVulnerability20]'s award-winning work  showed the utility of epistemically profiling networks. However, they relied on a proof-of-concept, closed-source implementation run on a small graph. `wisdom_of_crowds` was developed as a ground-up, open-source reimplementation in Python, optimized to be usable on much larger networks.

The field of computational philosophy [@sep-computational-philosophy] is in its infancy, and still lacks accessible tools. The primary tools used have been the closed-source program Laputa [@olsson2011simulation] and scripts written for the agent-based modelling Software NetLogo. The development of `wisdom_of_crowds` is not only valuable in its own right, but is meant as a push towards replicability and accessibility by the use of open-source Python tools.


# The `wisdom_of_crowds` package

The core of the `wisdom_of_crowds` package is a class `Crowd`. `Crowd` is initialized with a \textit{NetworkX} graph (encapsulating the social network's edges and nodes), and provides various functions to calculate derived metrics. Much of the heavy lifting is done by the `Crowd.is_mk_observer(n,m,k)`, which returns `True` just in case node $n$ is an $m,k$-observer.

Determining whether a node is an $m,k$-observer requires solving multiple shortest-path problems with a clique-finding problem. On the assumption that most uses will involve looping over many nodes in $G$, the combination of caching shortest paths and greedy clique-finding will minimize the overall computational effort needed [@VassilevskaEfficient09].

The remainder of the package are convenience functions for calculating and displaying various parameters defined by Sullivan et al.

 \autoref{fig:twitter} gives an example plot for a a real-life network of participants who retweeted content around the Black Lives Matter movement in the first half of 2020. Sullivan et al. used an earlier version of this dataset and were able to examine a network of 185 nodes. This analysis was run on a culled network of ~16k nodes and ~145k edges. Batch processing took about 6.25 hours on a 2017 desktop iMac.


# Discussion

Our results show that it is possible to replicate the methodology and outputs of Sullivan et al. in larger networks. As our package and its dependencies are all open source, this makes it possible for researchers in a range of fields (including philosophy, psychology, sociology, anthropology, communications, and network science) both to conduct new research and to re-analyze previously studied networks.

So far, the only networks that have been studied using this tool are from Twitter (and, as part of our testing framework, *de rigueur* standard social networks such as the Florentine Families network  [@breiger1986cumulated]. We anticipate that future research will expand the types of social networks under study. Other sources from social media such as Facebook, Reddit, and YouTube would all be viable candidates for study.  We expect that studies of friend networks, organizational networks in industry and the military, networks of sources used by journalists, criminal cartel networks, and academic citation networks would prove valuable.

The exploratory profiling made possible by our tool can reveal patterns of epistemic isolation and interaction across real-world networks, and suggests possibilities for more specific analyses.  By providing it to the community at large, we hope to facilitate further modelling of epistemic networks across a variety of domains.

![Sample output using built-in functions. Profile plots for entire network and subgroups looking at clusters (left) and topics (right). X axis is proportion of total, Y axis shows both S (height of bars) and $\pi$ (black line), plotted on a log scale.\label{fig:twitter}](twitterfigure.png)


# Acknowledgements

Work on this paper was supported by ARC Grant DP190101507 (to C.K. and M.A.) and by Templeton Grant 61378 (to M.A.)

# References
