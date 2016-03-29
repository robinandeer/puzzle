# Puzzle
Variant Caller GUI and genetic disease analysis tool.


## Overview

Puzzle will look for variant calling resources such as VCF files and [GEMINI][gemini] databases and visualize their content. It lets you inspect, annotate, and analyze variant calls.

Puzzle is not primarily meant to be run as a persistent server but think of it more as an web interface to quickly spin to visualize your variant calls.

We set out to make `Puzzle` both very simple to install as well as intuitive to use. You can be up and running in minutes with minimal prerequisites.

When puzzle is installed, in its simplest form it will try to visualize the VCF files in the directory you point to with

```bash
$ puzzle view tests/fixtures
```

Try it!

### Annotations ###

Puzzle will work best if the variants are annotated with [VEP][vep] or [SnpEff][snpeff], and some additional annotations such as 1000G frequencies and CADD scores.

### Gemini support ###

If the python package GEMINI is installed, the user can visualize a GEMINI database by running

```bash
$ puzzle view path/to/geminidatabase.db
```

### Persist information
Even though puzzle is not meant to be persistent, you can still save information in puzzle's database
for future querying running. First you need to initialize a puzzle database to store metainformation.

```bash
$ puzzle init --root path/to/dir
```

Default for root is `$USER/.puzzle`. When one or more databases are created they can be loaded with vcf files and or GEMINI databases.

### Loading

**VCFs**

```bash
$ puzzle load /path/to/your/file.vcf
```

**GEMINI databases**

```bash
$ puzzle load path/to/geminidatabase.db
```

## Developing Puzzle
Puzzle is a Python Flask app with a command line interface. It can work with multiple backends using plugins; raw VCFs, GEMINI, MongoDB.

Anyone can help make this project better - read [CONTRIBUTING](about/contributing.md) to get started!

[gemini]: https://github.com/arq5x/gemini
[vep]: http://www.ensembl.org/info/docs/tools/vep/index.html
[snpeff]: http://snpeff.sourceforge.net/SnpEff_manual.html
