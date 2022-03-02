---
title: '`wisdom_of_crowds`: A Python package for social-epistemological network profiling'
tags:
  - Python
  - epistemic networks
  - social epistemology
  - network epistemology
  - social epistemology
authors:
  - name: Colin Klein^[co-first author]^[corresponding author] # note this makes a footnote saying 'co-first author'
    orcid: 0000-0002-7406-4010
    affiliation: 1 # (Multiple affiliations must be quoted)
  - name: Marc Cheong^[co-first author] # note this makes a footnote saying 'co-first author'
    orcid: 0000-0002-0637-3436
    affiliation: 2
  - name: Marinus Ferreira
    orcid: 0000-0002-3571-9221
    affiliation: 3
  - name: Emily Sullivan
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

The epistemic position of an agent often depends on their position in a larger network of other agents who provide them with information. In general, agents are better off if they have diverse and independent sources. [@SullivanVulnerability20] developed a method for quantitatively characterizing the epistemic position of individuals in a network that takes into account both diversity and independence. Sullivan et al.'s work presented a proof-of-concept, closed-source implementation on a small graph derived from Twitter data. We present an ground up, open-source re-implementation of their concepts in Python, optimized to be usable on much larger networks.



# Statement of need

`wisdom_of_crowds`

`Gala` is an Astropy-affiliated Python package for galactic dynamics. Python
enables wrapping low-level languages (e.g., C) for speed without losing
flexibility or ease-of-use in the user-interface. The API for `Gala` was
designed to provide a class-based and user-friendly interface to fast (C or
Cython-optimized) implementations of common operations such as gravitational
potential and force evaluation, orbit integration, dynamical transformations,
and chaos indicators for nonlinear dynamics. `Gala` also relies heavily on and
interfaces well with the implementations of physical units and astronomical
coordinate systems in the `Astropy` package [@astropy] (`astropy.units` and
`astropy.coordinates`).

`Gala` was designed to be used by both astronomical researchers and by
students in courses on gravitational dynamics or astronomy. It has already been
used in a number of scientific publications [@Pearson:2017] and has also been
used in graduate courses on Galactic dynamics to, e.g., provide interactive
visualizations of textbook material [@Binney:2008]. The combination of speed,
design, and support for Astropy functionality in `Gala` will enable exciting
scientific explorations of forthcoming data releases from the *Gaia* mission
[@gaia] by students and experts alike.

# Mathematics

Single dollars ($) are required for inline mathematics e.g. $f(x) = e^{\pi/x}$

Double dollars make self-standing equations:

$$\Theta(x) = \left\{\begin{array}{l}
0\textrm{ if } x < 0\cr
1\textrm{ else}
\end{array}\right.$$

You can also use plain \LaTeX for equations
\begin{equation}\label{eq:fourier}
\hat f(\omega) = \int_{-\infty}^{\infty} f(x) e^{i\omega x} dx
\end{equation}
and refer to \autoref{eq:fourier} from text.

# Citations

Citations to entries in paper.bib should be in
[rMarkdown](http://rmarkdown.rstudio.com/authoring_bibliographies_and_citations.html)
format.

If you want to cite a software repository URL (e.g. something on GitHub without a preferred
citation) then you can do it with the example BibTeX entry below for @fidgit.

For a quick reference, the following citation commands can be used:
- `@author:2001`  ->  "Author et al. (2001)"
- `[@author:2001]` -> "(Author et al., 2001)"
- `[@author1:2001; @author2:2001]` -> "(Author1 et al., 2001; Author2 et al., 2002)"

# Figures

Figures can be included like this:
![Caption for example figure.\label{fig:example}](figure.png)
and referenced from text using \autoref{fig:example}.

Figure sizes can be customized by adding an optional second parameter:
![Caption for example figure.](figure.png){ width=20% }

# Acknowledgements

We acknowledge contributions from Brigitta Sipocz, Syrtis Major, and Semyeong
Oh, and support from Kathryn Johnston during the genesis of this project.

# References
