import logging
import os
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

import pytest

import kloch
import kloch_rezenv

LOGGER = logging.getLogger(__name__)

THISDIR = Path(__file__).parent

REZ_BASE_URL = "https://github.com/AcademySoftwareFoundation/rez/archive/refs/tags/{rez_version}.zip"

TESTS_CACHE_DIR = THISDIR / ".cache"
if not TESTS_CACHE_DIR.exists():
    print(f"mkdir({TESTS_CACHE_DIR})")
    TESTS_CACHE_DIR.mkdir()

REZ_INSTALL_CACHE = TESTS_CACHE_DIR / "rez"


def extract_zip(zip_path: Path, remove_zip=True):
    extract_root = zip_path.parent
    with zipfile.ZipFile(zip_path, "r") as zip_file:
        zip_file.extractall(extract_root)

    if remove_zip:
        zip_path.unlink()

    return extract_root


def install_rez(
    rez_version: str,
    python_executable: Path,
    target_dir: Path,
) -> Path:
    """
    Create a rez installation with the given configuration.

    Args:
        rez_version: full rez version to download from GitHub
        python_executable: filesystem path to the python executable to install rez with.
        target_dir: filesystem path to an empty existing directory

    Returns:
        filesystem path to the rez executable in the ``target_dir``.
    """
    rez_url = REZ_BASE_URL.format(rez_version=rez_version)
    rez_tmp_dir = target_dir / "__installer"
    rez_tmp_dir.mkdir()
    rez_zip_path = target_dir / "rez.zip"

    LOGGER.info(f"downloading '{rez_url}' to '{rez_zip_path}' ...")
    with urllib.request.urlopen(rez_url) as dl_stream, rez_zip_path.open(
        "wb"
    ) as dl_file:
        shutil.copyfileobj(dl_stream, dl_file)

    rez_root = extract_zip(zip_path=rez_zip_path, remove_zip=True)
    rez_installer_path = rez_root / f"rez-{rez_version}" / "install.py"
    rez_command = [
        str(python_executable),
        str(rez_installer_path),
        str(target_dir),
    ]
    LOGGER.info(f"installing rez to '{target_dir}'")
    LOGGER.debug(f"subprocess.run({rez_command})")
    result = subprocess.run(
        rez_command,
        check=True,
    )
    shutil.rmtree(rez_tmp_dir)


@pytest.mark.slow
def test__e2e_kloch_rezenv(tmp_path, data_dir):

    rez_version = "2.114.1"

    if not REZ_INSTALL_CACHE.exists():
        REZ_INSTALL_CACHE.mkdir()
        try:
            install_rez(rez_version, Path(sys.executable), REZ_INSTALL_CACHE)
        except Exception:
            shutil.rmtree(REZ_INSTALL_CACHE)
            raise
    else:
        print(f"found rez already installed at {REZ_INSTALL_CACHE}")

    if sys.platform in ("win32", "cygwin"):
        rez_bin_dir = REZ_INSTALL_CACHE / "Scripts" / "rez"
        check_command = ["--", "echo", "$Env:REZ_VERSION", "$Env:TESTPKG_CONFIRM_VAR"]
    else:
        rez_bin_dir = REZ_INSTALL_CACHE / "bin" / "rez"
        check_command = ["--", "echo", "$REZ_VERSION\n$TESTPKG_CONFIRM_VAR"]

    environ = os.environ.copy()
    environ[kloch.Environ.CONFIG_LAUNCHER_PLUGINS] = kloch_rezenv.__name__
    environ[kloch.Environ.CONFIG_CLI_SESSION_PATH] = str(tmp_path)
    environ[kloch.Environ.CONFIG_PROFILE_ROOTS] = str(data_dir)
    environ["__TEST_REZ_INSTALL_DIR"] = str(rez_bin_dir)
    environ["REZ_PACKAGES_PATH"] = str(data_dir / "rezrepo")

    command = [
        sys.executable,
        "-m",
        "kloch",
        "run",
        "rezenv-plugin-test",
        "--debug",
    ]
    command += check_command
    result = subprocess.run(command, env=environ, capture_output=True, text=True)
    print("=== [stdout] ===")
    print(result.stdout)
    print("=== [stderr] ===")
    print(result.stderr)
    assert not result.returncode
    # "CONFIRMED" from ./data/rezrepo/testpkg/1.2.3/package.py
    expected = rez_version + "\nCONFIRMED"
    assert expected in result.stdout
