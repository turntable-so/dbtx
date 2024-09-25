import os
import subprocess
import sys

DBT_PROJECT_DIR = "tests/jaffle_shop_duckdb"
BASE_ENV = {"DBT_PROJECT_DIR": DBT_PROJECT_DIR}


def run_cli(command: list[str], env: dict[str, str] = {}):
    return subprocess.run(
        [sys.executable, "main.py", *command],
        capture_output=True,
        text=True,
        env={**env, **os.environ},
    )


def test_runner_fails_in_wrong_dir():
    res = run_cli(["--version"])
    assert res.returncode == 1
    assert "Could not find dbt_project.yml file." in res.stderr


def test_runner_fails_no_command():
    res = run_cli([])
    assert res.returncode == 1
    assert "No dbt command provided" in res.stderr


def test_runner_succeeds_in_correct_dir():
    res = run_cli(["--version"], env=BASE_ENV)
    assert res.returncode == 0
    assert "duckdb" in res.stdout


def test_version_specification_with_env():
    res = run_cli(["--version"], env={**BASE_ENV, "DBT_VERSION": "1.5"})
    assert res.returncode == 0
    assert "1.5" in res.stdout
