from puzzle.cli import base as cli
from click.testing import CliRunner

def test_base_command():
    runner = CliRunner()
    result = runner.invoke(cli, [])
    
    assert result.exit_code == 0
