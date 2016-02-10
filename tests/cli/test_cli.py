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
        result = runner.invoke(cli, ['load','--root', puzzle_dir, 
                                     '-m', 'gemini', gemini_db_path])
        
        assert result.exit_code == 0

    def test_load_command_no_db(self, dir_path, vcf_file):
        """Test to load a gemini db"""
        
        logger = logging.getLogger("test_load_command_no_db")
        runner = CliRunner()
        logger.debug("Test load a vcf when no database")
        result = runner.invoke(cli, ['load','--root', dir_path, vcf_file])
        
        #Should exit since db does not exist
        assert result.exit_code == 1

    def test_load_command_false_gemini_db(self, puzzle_dir, vcf_file):
        """Test to load a gemini db"""
        
        logger = logging.getLogger("test_load_command_false_gemini_db")
        runner = CliRunner()
        logger.debug("Test load a gemini db but not a valid gemini db")
        result = runner.invoke(cli, ['load','--root', puzzle_dir, 
                                     '-m', 'gemini', vcf_file])
        
        #Should exit since db is not a gemini db
        assert result.exit_code == 1

class TestCasesCommand:
    """Test the cli cases command"""
    pass
