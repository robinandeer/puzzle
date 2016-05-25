# Development
Puzzle is built as a Flask app with an emphasis on server rendering of templates. This is a concious decision to make maintainance as easy as possible.

The list of variants is the most prominent example where we deviate from the above ideal. This is in order to build a reactive interface that let's the user quickly sort and filter the 1000s of variants that are loaded on each request.

## Development environment
We use [(mini)conda](http://conda.pydata.org/miniconda.html) for developing Puzzle. It's easy to set up and makes installing all kinds of dependencies a breeze.

Puzzle will soon be available as a conda install through the [bioconda](https://bioconda.github.io/) initiative.

## Separation of concern
We try to keep a strict separation between the backend and consumers (server, CLI).
