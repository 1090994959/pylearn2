==============================
Pylearn2: The Machine Learning Research Library
==============================

Pylearn2 is a library designed to make machine learning research easy.

The Pylearn2 `documentation <http://deeplearning.net/software/pylearn2/>`_.

Pylearn2 was initially developed by David
Warde-Farley, Pascal Lamblin, Ian Goodfellow and others during the winter
2011 offering of `IFT6266 <http://www.iro.umontreal.ca/~pift6266/>`_, and
is now developed by the LISA lab.


Quick start and basic design rules
------------------

- Subscribe to the `pylearn-dev Google group
  <http://groups.google.com/group/pylearn-dev>`_ for important updates. Please write
  to this list for troubleshooting help or any feedback you have about the library,
  even if you're not a Pylearn2 developer.
- There are `examples <https://github.com/lisa-lab/pylearn/tree/master/pylearn2/scripts/train_example>`_.
  They cover how to create a dataset and how to train and how to inspect the model.
- Pylearn2 should not force users to commit to the whole library. If someone just wants
  to implement a Model, they should be able to do that and not need to implement
  a TrainingAlgorithm. Try not to write library features that force users to buy into
  the whole library.
- When writing reference implementations to go in the library, maximize code re-usability
  by decomposing your algorithm into a TrainingAlgorithm that trains a Model on a Dataset.
  It will probably do this by minimizing a Cost.


If you want to build a local copy of the documentation, run
    python ./doc/scripts/docgen.py

