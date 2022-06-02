from setuptools import setup, find_packages


setup(
    name='wisdom_of_crowds',
    version='1.01.2',
    description='Re-implementation and extension of the measures described in Sullivan et al. (2020): Vulnerability in Social Epistemic Networks, International Journal of Philosophical Studies',
    license='GPL3.0',
    author="Colin Klein and Marc Cheong",
    author_email='Colin.Klein@anu.edu.au',
    packages=find_packages('wisdom_of_crowds'),
    py_modules=['wisdom_of_crowds'],
    package_dir={'': 'src'},
    url='https://github.com/cvklein/wisdom-of-crowds',
    keywords='wisdom crowds epistemology network',
    install_requires=[
          'networkx>=2.6',
          'matplotlib>=3.5',
          'pytest>=7.0',
      ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Sociology',
    ],
    python_requires='>=3.7',
)
