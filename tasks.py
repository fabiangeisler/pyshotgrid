"""
Tasks for maintaining the project.

Execute 'invoke --list' for guidance on using Invoke
"""
# Core Library modules
import shutil
import webbrowser

# noinspection PyCompatibility
from pathlib import Path

# Third party modules
from invoke import task

ROOT_DIR = Path(__file__).parent
TEST_DIR = ROOT_DIR / "tests"
SRC_DIR = ROOT_DIR / "src"

DOC_DIR = ROOT_DIR / "docs"
DOCS_BUILD_DIR = DOC_DIR / "_builds"
DOCS_INDEX = DOCS_BUILD_DIR / "index.html"

COVERAGE_INDEX = ROOT_DIR / "htmlcov" / "index.html"

BUILD_FROM = ROOT_DIR / "."
DIST_SOURCE = ROOT_DIR / "dist" / "*"


def _delete_director(items_to_delete):
    """Utility function to delete files or directories."""
    for item in items_to_delete:
        if item.is_dir():
            shutil.rmtree(item, ignore_errors=True)
        elif item.is_file():
            item.unlink()
        else:
            # noinspection PyCompatibility
            raise ValueError(f"{item} is not a directory or a file")


def _finder(directory, item, exclusions=None):
    """
    Utility function to generate a Path list of files based on globs.

    :param Path directory: Base directory to search from.
    :param str item: Specify glob pattern to delete
    :param list[str]|None exclusions: Specify pathlib objects to exclude from deletion
     (can be directories of files)
    """
    exclusions = exclusions or []
    item_list = list(directory.rglob(item))
    for exc in exclusions:
        if exc in item_list:
            item_list.remove(exc)
    if item_list:
        _delete_director(item_list)


def _clean_mypy():
    """Clean up mypy cache and results."""
    patterns = [
        ".mypy_cache",
        "mypy-report",
    ]
    for pattern in patterns:
        _finder(ROOT_DIR, pattern)


def _clean_build():
    """Clean up build artifacts."""
    patterns = [
        "build/",
        "dist/",
        ".eggs/",
        "*egg-info",
        "*.egg",
    ]
    for pattern in patterns:
        _finder(ROOT_DIR, pattern)


def _clean_test():
    """Clean up test artifacts."""
    patterns = [
        ".pytest_cache",
        "htmlcov",
        ".coverage",
        "coverage.xml",
        "pytest-report.html",
    ]
    for pattern in patterns:
        _finder(ROOT_DIR, pattern)


def _clean_python():
    """Clean up python file artifacts."""
    patterns = ["*.pyc", "*.pyo", "__pycache__"]
    for pattern in patterns:
        _finder(ROOT_DIR, pattern)


def _clean_docs():
    """Clean the document build."""
    _finder(DOC_DIR, "_build")


def _clean_ruff():
    """Clean the ruff cache files."""
    patterns = [
        ".ruff_cache",
    ]
    for pattern in patterns:
        _finder(ROOT_DIR, pattern)


@task()
def clean(c):
    """Removes all test, build, log and lint artifacts from the environment."""
    _clean_mypy()
    _clean_build()
    _clean_python()
    _clean_test()
    _clean_docs()
    _clean_ruff()


@task(
    name="ruff-format",
    aliases=("bl", "black"),
    help={
        "check": "Checks if source would be reformatted without applying changes.",
    },
)
def ruff_format(c, check=False):
    """Runs "ruff format" against the code base. Which formats it in black code style."""
    print("Run 'ruff format'")
    black_options = ["--diff", "--check"] if check else []
    # noinspection PyCompatibility
    c.run(f"ruff format {' '.join(black_options)} .")


@task(
    name="ruff-check",
    aliases=("ruff",),
    help={
        "fix": "Attempt to fix found code issues.",
    },
)
def ruff_check(c, fix=False):
    """Run ruff against selected files."""
    print("Run 'ruff'")
    c.run(f"ruff check {SRC_DIR} {TEST_DIR} {'--fix' if fix else ''}")


@task()
def mypy(c):
    """Run mypy against the code base."""
    print("Run 'mypy'")
    # noinspection PyCompatibility
    # In order for mypy to find the pyproject.toml we need to execute it from
    # the root directory.
    with c.cd(ROOT_DIR):
        c.run(f"mypy {SRC_DIR}")


@task(pre=[ruff_format, ruff_check, mypy])
def lint(c):
    """Run all lint tasks."""


@task(
    name="tox",
    aliases=(
        "test",
        "tests",
    ),
    help={
        "env": "The tox environment(s) to run.",
    },
)
def tox(c, env=""):
    """Run tests using pytest."""
    _clean_test()
    c.run(f"tox {'-e ' + env if env else ''}")


@task(
    aliases=("cov",),
    help={
        "open_browser": "Open the docs in the web browser",
    },
)
def coverage(c, open_browser=False):
    c.run("pytest --cov-report html --cov-report term", warn=True)
    if open_browser:
        webbrowser.open(str(COVERAGE_INDEX))


@task(
    help={
        "open_browser": "Open the docs in the web browser",
    },
)
def docs(c, open_browser=False):
    """Build documentation."""
    _clean_docs()
    c.run("tox -e py310_docs")
    if open_browser:
        webbrowser.open(str(DOCS_INDEX))


@task()
def build(c):
    """Creates a new sdist & wheel build using the PyPI tool."""
    _clean_build()
    # noinspection PyCompatibility
    c.run(f'python -m build "{BUILD_FROM}"')


@task(pre=[build])
def pypi_test(c):
    """Uploads a build to the PyPI-test python repository."""
    # noinspection PyCompatibility
    c.run(f'python -m twine upload -r testpypi "{DIST_SOURCE}"')


@task(pre=[build])
def pypi(c):
    """Uploads a build to the PyPI python repository."""
    # noinspection PyCompatibility
    c.run(f'python -m twine upload "{DIST_SOURCE}"')


@task()
def pre_commit_update(c):
    """Updates the pre-commit development environment"""
    c.run("pre-commit clean")
    c.run("pre-commit gc")
    c.run("pre-commit autoupdate")


# @task
# def psr(c):
#     """Runs semantic-release publish."""
#     _clean_build()
#     c.run("semantic-release publish")
