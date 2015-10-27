# Puzzle
Variant Caller GUI and genetic disease analysis tool.


## Overview

Puzzle will look for variant calling resources such as VCF files and [GEMINI](gemini) databases and visualize their content. It lets you inspect, annotate, and analyze variant calls.

Puzzle is not primarily meant to be run as a persistant server but think of it more as an webinterface to quickly spin to visualize your variant calls.

We set out to make `Puzzle` both very simple to install as well as intuitive to use. You can be up and running in minutes with minimal prerequisites.

When puzzle is installed, in its simplest form it will try to visualize the VCF files in the directory you point to with

```
puzzle tests/ view
```

Try it!

### Annotations ###

Puzzle will work best if the variants are annotated with [VEP](http://www.ensembl.org/info/docs/tools/vep/index.html), and some additional annotations such as 1000G frequencies and CADD scores.

### Gemini support ###

If gemini is installed, the user can visualize a gemini database by running

```
puzzle path/to/geminidatabase.db --plugin gemini view
```

Right now it will only work well with databases that includes one family.

## Developing Puzzle
Puzzle is a Python Flask app with a command line interface. It can work with multiple backends using plugins; raw VCFs, GEMINI, MongoDB.

Anyone can help make this project better - read [CONTRIBUTING](about/contributing.md) to get started!

[gemini]: https://github.com/arq5x/gemini
