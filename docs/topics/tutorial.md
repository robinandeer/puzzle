# Tutorial
There are some demo files included in the repository. Let's use them to demonstrate how Puzzle can visualize variant resources like VCF files and GEMINI databases.

## 1. Setup

```bash
$ pip install puzzle
$ git clone https://github.com/robinandeer/puzzle
```

## 2. Start the Puzzle server

```bash
$ puzzle view ./puzzle/tests/
[...]
Flask serving on http://localhost:5000/
```

Go to `http://localhost:5000/` in your web browser to connect to the Puzzle interface. It will display a list of VCF files as "cases".

## 3. Navigating the interface
You can now navigate the interface and interact by associating HPO terms with individuals under investigation, write comments, upload associated images, etc.

> Note that all the changes will _not_ be persited once you close the server. For that we need to follow the next step in the tutoria.

## 4. Loading cases
Puzzle also supports persistant storage of comments etc. and can be used to keep track of VCF files spread across you file system. To get started you need to initialize a puzzle database.

```bash
$ puzzle init
```

This command will create a database under `$USER/.puzzle`. You can now load VCF files with assciated PED files.

```bash
$ puzzle load ./puzzle/tests/fixtures/hapmap.vcf -f ./puzzle/tests/fixtures/hapmap.ped
```

When you now bring up the interface:

```bash
$ puzzle view
```

You will see a single case listed in the first view. The name of the case is fetched from the PED file. If you click the case, you will further find more details filled in about the relationship between samples.

> Loading a GEMINI database doesn't require a PED file since all the information is contained within the GAMINI database itself.

## 5. Conclusions
That's about it for the brief tutorial! Puzzle isn't more complex than this but there is plenty of features which are best found out by exploring the interface.
