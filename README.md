# Puzzle [![Build Status][travis-image]][travis-url] [![Test Coverage][coveralls-img]][coveralls-url]

Variant Caller GUI and genetic disease analysis tool.

Documentation: https://robinandeer.gitbooks.io/puzzle/content/

```bash
$ pip install puzzle
$ wget http://bit.ly/puzzle-bosc
$ unzip puzzle-bosc && rm -r puzzle-bosc
$ puzzle view ./puzzle-demo
```

## Using Puzzle
Puzzle will look for variant calling resources such as VCF files and [GEMINI][gemini] databases and visualize their contents. It lets you inspect, annotate, and analyze variant calls.

Puzzle is not primarily meant to be run as a persistent server but think of it more as an web interface to quickly spin up to visualize variant calls.

We set out to make `Puzzle` very simple to install and intuitive to use. You should be up and running in minutes with minimal prerequisites.

## Developing Puzzle
Puzzle is a Python Flask app with a command line interface. It works with multiple backends using plugins; raw VCFs, GEMINI, MongoDB.

Anyone can help make this project better - read [CONTRIBUTING](CONTRIBUTING.md) to get started!

## Testing Puzzle
To run the tests, you need [pytest][pytest] installed. You can install `pytest` together
with the other development libraries by running `pip install -r requirements-dev.txt`.

You will also need to download the database used for testing, which you can do by executing this command:

```bash
$ wget https://s3-us-west-2.amazonaws.com/robinandeer/HapMapFew.db -O tests/fixtures/HapMapFew.db
```

To test a GEMINI database with structural variants do:

```bash
$ wget https://s3-us-west-2.amazonaws.com/robinandeer/HapMapSv.db -O tests/fixtures/HapMapSv.db
```

Then, just run `py.test tests/`

## Use ped info ##

Puzzle uses the PED format to show more information in family view and in variant calls:

```bash
$ puzzle view tests/fixtures/hapmap.vcf --family_file tests/fixtures/hapmap.ped
```

## Build documentation
Documentation is generated using [Gitbook][gitbook]. Building the docs locally requires the GitBook CLI.

```bash
$ cd puzzle/
$ npm install -g gitbook-cli
$ gitbook serve ./docs
```

The documentation can now be viewed on `http://localhost:4000/`.

## Credits
Puzzle Piece by Creative Stall from the Noun Project

## License
MIT. See the [LICENSE](LICENSE) file for more details.


[travis-url]: https://travis-ci.org/robinandeer/puzzle?branch=master
[travis-image]: https://img.shields.io/travis/robinandeer/puzzle/master.svg?style=flat-square
[coveralls-url]: https://coveralls.io/github/robinandeer/puzzle
[coveralls-img]: https://img.shields.io/coveralls/robinandeer/puzzle.svg?style=flat-square
[gemini]: https://github.com/arq5x/gemini
[pytest]: http://pytest.org/latest/
[gitbook]: https://www.gitbook.com/
