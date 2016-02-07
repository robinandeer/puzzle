from puzzle.cli import cli
from click.testing import CliRunner

def test_base_command():
    runner = CliRunner()
    result = runner.invoke(cli, [])
    
    assert result.exit_code == 0

# def test_base_command_with_root():
#     runner = CliRunner()
#     result = runner.invoke(cli, ['--root','tests/fixtures'])
#
#     assert result.exit_code == 0