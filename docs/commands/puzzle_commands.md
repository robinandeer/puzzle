# puzzle #

```
$ puzzle --help
Usage: puzzle [OPTIONS] COMMAND [ARGS]...

  Puzzle: manage DNA variant resources.

Options:
  --version          Show the version and exit.
  -v, --verbose
  -c, --config PATH
  --help             Show this message and exit.

Commands:
  cases        Show all cases in the database.
  delete       Delete a case or individual from the...
  individuals  Show all individuals in the database.
  init         Initialize a database that store metadata...
  load         Load a variant source into the database.
  view         Visualize DNA variant resources.
```

## init ##

```
$ puzzle init --help
Usage: puzzle init [OPTIONS]

  Initialize a database that store metadata

  Check if "root" dir exists, otherwise create the directory and build the
  database. If a database already exists, do nothing.

Options:
  --reset               Wipe the database and initialize a new one
  -r, --root PATH       Path to where to find variant source(s)
  --phenomizer TEXT...  Phenomizer username/password
  --help                Show this message and exit.
```

[Phenomizer](phenomizer) needs login credentials, please send an email to sebastian.koehler@charite.de to get credentials.
The login will be stored in the database when added with `--phenomizer` option.


[phenomizer]: http://compbio.charite.de/phenomizer/

## cases ##

```
$ puzzle cases --help
Usage: puzzle cases [OPTIONS]

  Show all cases in the database.

  If no database was found run puzzle init first.

Options:
  -r, --root PATH  Path to where to find variant source(s)
  --help           Show this message and exit.
```

## individuals ##

```
$ puzzle individuals --help
Usage: puzzle individuals [OPTIONS]

  Show all individuals in the database.

  If no database was found run puzzle init first.

Options:
  -r, --root PATH  Path to where to find variant source(s)
  --help           Show this message and exit.
```

## delete ##

```
$ puzzle delete --help
Usage: puzzle delete [OPTIONS]

  Delete a case or individual from the database.

  If no database was found run puzzle init first.

Options:
  -f, --family_id TEXT
  -i, --individual_id TEXT
  -r, --root PATH           Path to where to find variant source(s)
  --help                    Show this message and exit.
```

## load ##

```
$ puzzle load --help
Usage: puzzle load [OPTIONS] VARIANT_SOURCE

  Load a variant source into the database.

  If no database was found run puzzle init first.

  1. VCF: If a vcf file is used it can be loaded with a ped file 
  2. GEMINI: Ped information will be retreived from the gemini db

Options:
  -f, --family_file FILENAME
  --family_type [ped|alt]     If the analysis use one of the known setups,
                              please specify which one.  [default: ped]
  -r, --root PATH             Path to where to find variant source(s)
  -m, --mode [vcf|gemini]     [default: vcf]
  --variant-type [snv|sv]     If Structural Variantion or Single Nucleotide
                              variant mode should be used  [default: snv]
  --help                      Show this message and exit.
```

## view ##

```
$ puzzle view --help
Usage: puzzle view [OPTIONS] [VARIANT_SOURCE]

  Visualize DNA variant resources.

  1. Look for variant source(s) to visualize and instantiate the right plugin

Options:
  --host TEXT                 [default: 0.0.0.0]
  --port INTEGER              [default: 5000]
  --debug
  -p, --pattern TEXT          [default: *.vcf]
  --no-browser                Prevent auto-opening browser
  --phenomizer TEXT...        Phenomizer username/password
  -f, --family_file FILENAME
  --family_type [ped|alt]     If the analysis use one of the known setups,
                              please specify which one.  [default: ped]
  --version                   Show the version and exit.
  -r, --root PATH             Path to where to find variant source(s)
  -m, --mode [vcf|gemini]     [default: vcf]
  --variant-type [snv|sv]     If Structural Variantion or Single Nucleotide
                              variant mode should be used  [default: snv]
  --help                      Show this message and exit.
```

This command can be used to view a puzzle database or one or more puzzle databases.
To view a puzzle database just run `puzzle view` or `puzzle view --root path/to/puzzle-dir`.
If one or more sources should be viewed specify the path to a variant source or a directory with variant sources like `puzzle view path/to/my.vcf`