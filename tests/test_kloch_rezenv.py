import os
import stat
import subprocess
import sys
from typing import Dict
from typing import List

import pytest

from kloch_rezenv import RezEnvLauncher
from kloch_rezenv import RezEnvLauncherSerialized


def test__RezEnvLauncher(monkeypatch, tmp_path):
    class Results:
        command: List[str] = None
        env: Dict[str, str] = None

    def patched_subprocess(command, env, *args, **kwargs):
        Results.env = env
        Results.command = command
        return subprocess.CompletedProcess(command, 0)

    rezenv_dir = tmp_path / "bin"
    rezenv_dir.mkdir()
    if sys.platform in ("win32", "cygwin"):
        rezenv_path = rezenv_dir / "rez-env.EXE"
    else:
        rezenv_path = rezenv_dir / "rez-env"
    rezenv_path.write_text("echo placeholder")
    current_stats = os.stat(rezenv_path)
    os.chmod(rezenv_path, current_stats.st_mode | stat.S_IEXEC)

    monkeypatch.setattr(subprocess, "run", patched_subprocess)
    environ_new_path = str(rezenv_dir) + os.pathsep + os.environ.get("PATH", "")
    monkeypatch.setenv("PATH", environ_new_path)

    launcher = RezEnvLauncher(
        requires={"maya": "2023", "houdini": "20.2"},
        params=["--verbose"],
        config={},
        environ=os.environ.copy(),
    )

    launcher.execute(tmpdir=tmp_path, command=["maya"])

    assert Results.command[0] == str(rezenv_path)
    assert Results.command[-1] == "maya"
    assert "maya-2023" in Results.command
    assert "--verbose" in Results.command


def test__RezEnvLauncherSerialized(data_dir, monkeypatch):
    src_dict = {}
    instance = RezEnvLauncherSerialized(src_dict)
    instance.validate()

    src_dict = {
        "requires": {"python": "3.9", "maya": "2023+"},
        "config": str(data_dir),
    }
    instance = RezEnvLauncherSerialized(src_dict)
    with pytest.raises(AssertionError) as error:
        instance.validate()
        assert "must be a dict" in error

    src_dict = {
        "requires": {"python": "3.9", "maya": "2023+"},
    }
    instance = RezEnvLauncherSerialized(src_dict)
    instance.validate()
    assert instance["requires"] == {"python": "3.9", "maya": "2023+"}
