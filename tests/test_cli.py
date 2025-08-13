import subprocess, sys

def test_cli_help():
    # just verify module loads and prints help
    cmd = [sys.executable, "-m", "lsd_music_gradients.cli", "--help"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0
    assert "connectivity" in res.stdout
