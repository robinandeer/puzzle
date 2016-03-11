import os
import logging

from puzzle.cli import base as cli
from click.testing import CliRunner


class TestBaseCommand:
    """Test the cli base command"""

    def test_base_command(self):
        logger = logging.getLogger("test_base_command")
        runner = CliRunner()
        logger.debug("Test to run base command without arguments")
        result = runner.invoke(cli, [])

        assert result.exit_code == 0

class TestInitCommand:
    """Test the cli init command"""

    def test_init_command(self, dir_path):
        logger = logging.getLogger("test_init_command")
        runner = CliRunner()
        logger.debug("Test initalize a puzzle repo")
        result = runner.invoke(cli, ['init','--root', dir_path])

        assert os.path.exists(dir_path)

    def test_init_command_file(self):
        logger = logging.getLogger("test_init_command_file")
        file_path = "tests/fixtures/hapmap.ped"
        runner = CliRunner()
        logger.debug("Test initalize a puzzle repo")
        result = runner.invoke(cli, ['init','--root', file_path])

        #Can not initialize with file...
        assert result.exit_code == 1

    def test_init_command_existing_dir(self, puzzle_dir):
        logger = logging.getLogger("test_init_command_existing_dir")
        runner = CliRunner()
        logger.debug("Test initalize a existing puzzle repo")
        result = runner.invoke(cli, ['init','--root', puzzle_dir])

        #Should exit since dir already exists
        assert result.exit_code == 1


class TestLoadCommand:
    """Test the cli load command"""

    def test_load_command_vcf(self, puzzle_dir, vcf_file):
        """Test to load a vcf without any ped file"""

        logger = logging.getLogger("test_load_command_vcf")
        runner = CliRunner()
        logger.debug("Test load a vcf")
        result = runner.invoke(cli, ['load','--root', puzzle_dir, vcf_file])

        assert result.exit_code == 0

    def test_load_command_vcf_with_ped(self, puzzle_dir, vcf_file, ped_file):
        """Test to load a vcf with ped file"""

        logger = logging.getLogger("test_load_command_vcf_with_ped")
        runner = CliRunner()
        logger.debug("Test load a vcf with a ped file")
        result = runner.invoke(cli, ['load','--root', puzzle_dir, '-f', ped_file, vcf_file])

        assert result.exit_code == 0

    def test_load_command_gemini(self, puzzle_dir, gemini_db_path):
        """Test to load a gemini db"""

        logger = logging.getLogger("test_load_command_gemini")
        runner = CliRunner()
        logger.debug("Test load a gemini db")
        result = runner.invoke(cli, ['load','--root', puzzle_dir, gemini_db_path])

        assert result.exit_code == 0

    def test_load_command_no_db(self, dir_path, vcf_file):
        """Test to load a gemini db"""

        logger = logging.getLogger("test_load_command_no_db")
        runner = CliRunner()
        logger.debug("Test load a vcf when no database")
        result = runner.invoke(cli, ['load','--root', dir_path, vcf_file])
        
        db_path = os.path.join(dir_path, 'puzzle_db.sqlite3')
        
        #Should exit since db does not exist
        assert result.exit_code == 1

class TestCasesCommand:
    """Test the cli cases command"""

    def test_cases_command(self, populated_puzzle_db):
        """Check if cases command work"""

        logger = logging.getLogger("test_cases_command")
        runner = CliRunner()
        logger.debug("Test if cases command work")
        result = runner.invoke(cli, ['cases','--root', populated_puzzle_db])

        assert result.exit_code == 0
        assert 'hapmap.vcf' in result.output

    def test_cases_command_file(self, vcf_file):
        """Check if cases command work"""

        logger = logging.getLogger("test_cases_command_file")
        runner = CliRunner()
        logger.debug("Test if cases command work with a file")
        result = runner.invoke(cli, ['cases','--root', vcf_file])

        assert result.exit_code == 1

    def test_cases_command_no_db(self, dir_path):
        """Check if cases command work"""

        logger = logging.getLogger("test_cases_no_db")
        runner = CliRunner()
        logger.debug("Test if cases command work without a puzzle db")
        result = runner.invoke(cli, ['cases','--root', dir_path])

        assert result.exit_code == 1

class TestIndividualsCommand:
    """Test the cli individuals command"""

    def test_individuals_command(self, populated_puzzle_db):
        """Check if cases command work"""

        logger = logging.getLogger("test_individuals_command")
        runner = CliRunner()
        logger.debug("Test if individuals command work")
        result = runner.invoke(cli, ['individuals','--root', populated_puzzle_db])

        assert result.exit_code == 0
        assert "ADM1059A1" in result.output

    def test_individuals_command_file(self, vcf_file):
        """Check if cases command work"""

        logger = logging.getLogger("test_individuals_command_file")
        runner = CliRunner()
        logger.debug("Test if individuals command work with a file")
        result = runner.invoke(cli, ['individuals','--root', vcf_file])

        assert result.exit_code == 1

    def test_individuals_command_no_db(self, dir_path):
        """Check if cases command work"""

        logger = logging.getLogger("test_individuals_no_db")
        runner = CliRunner()
        logger.debug("Test if individuals command work without a puzzle db")
        result = runner.invoke(cli, ['individuals','--root', dir_path])

        assert result.exit_code == 1

class TestDeleteCommand:
    """Test the cli delete command"""

    def test_delete_individual(self, populated_puzzle_db):
        """Check if delete individuals command work"""

        logger = logging.getLogger("test_delete_individual")
        runner = CliRunner()
        logger.debug("Test if delete individuals command work")
        result = runner.invoke(cli, ['delete','--root', populated_puzzle_db,
                                     '-i', 'ADM1059A1'])

        assert result.exit_code == 0

    def test_delete_case(self, populated_puzzle_db):
        """Check if delete individuals command work"""

        logger = logging.getLogger("test_delete_case")
        runner = CliRunner()
        logger.debug("Test if delete case command work")
        result = runner.invoke(cli, ['delete','--root', populated_puzzle_db,
                                     '-f', '636808'])

        assert result.exit_code == 0

    def test_delete_command_file(self, vcf_file):

        runner = CliRunner()
        result = runner.invoke(cli, ['delete','--root', vcf_file,
                                     '-f', '636808'])

        assert result.exit_code == 1

    def test_delete_command_no_input(self, populated_puzzle_db):

        runner = CliRunner()
        result = runner.invoke(cli, ['delete','--root', populated_puzzle_db])

        assert result.exit_code == 1

    def test_delete_command_non_existing_case(self, populated_puzzle_db):

        runner = CliRunner()
        result = runner.invoke(cli, ['delete','--root', populated_puzzle_db,
                                     '-f', 'hello'])

        assert result.exit_code == 1

    def test_delete_command_non_existing_individual(self, populated_puzzle_db):

        runner = CliRunner()
        result = runner.invoke(cli, ['delete','--root', populated_puzzle_db,
                                     '-i', 'hello'])

        assert result.exit_code == 1

