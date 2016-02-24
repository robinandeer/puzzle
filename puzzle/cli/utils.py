import click
import puzzle

root = click.option('--root', '-r',
                        type=click.Path(),
                        help="Path to where to find variant source(s)"
                    )

mode = click.option('-m', '--mode',
                        type=click.Choice(['vcf', 'gemini']),
                        default='vcf',
                        show_default=True
                        )

verbose = click.option('-v', '--verbose',
                        count=True,
                        default=2
                        )

variant_type = click.option('--variant-type',
                type=click.Choice(['snv', 'sv']),
                default='snv',
                show_default=True,
                help="If Structural Variantion or Single Nucleotide variant"\
                " mode should be used"
                )
family_file = click.option('-f', '--family_file',
                type=click.File('r')
                )
family_type = click.option('--family_type',
                type=click.Choice(['ped', 'alt']),
                default='ped',
                show_default=True,
                help='If the analysis use one of the known setups, please specify which one.'
)
version = click.version_option(puzzle.__version__)

phenomizer = click.option('--phenomizer', 
                nargs=2, 
                help='Phenomizer username/password',
                envvar='PHENOMIZER_AUTH'
                )