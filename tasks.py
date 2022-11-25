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
from invoke import call, task

ROOT_DIR = Path(__file__).parent
TEST_DIR = ROOT_DIR / "tests"
SRC_DIR = ROOT_DIR / "src"

DOC_DIR = ROOT_DIR / "docs"
DOCS_BUILD_DIR = DOC_DIR / "_build"
DOCS_INDEX = DOCS_BUILD_DIR / "index.html"

BUILD_FROM = ROOT_DIR / "."
DIST_SOURCE = ROOT_DIR / "dist" / "*"


PYTHON_FILES_ALL = list(ROOT_DIR.rglob("*.py"))
PYTHON_FILES_ALL.remove(ROOT_DIR / "tasks.py")
PYTHON_FILES_ALL_STR = ""
for file in PYTHON_FILES_ALL:
    PYTHON_FILES_ALL_STR = "".join([PYTHON_FILES_ALL_STR, '"', str(file), '" '])

PYTHON_FILES_SRC = list(SRC_DIR.rglob("*.py"))
PYTHON_FILES_SRC_STR = ""
for file in PYTHON_FILES_SRC:
    PYTHON_FILES_SRC_STR = "".join([PYTHON_FILES_SRC_STR, '"', str(file), '" '])


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
    patterns = ["_build", "jupyter_execute", "*.css"]
    for pattern in patterns:
        _finder(ROOT_DIR, pattern)


def _clean_flake8():
    """Clean the bandit report files."""
    patterns = [
        "flake-report/",
        "*report.html",
        "*source.html",
    ]
    for pattern in patterns:
        _finder(ROOT_DIR, pattern)


@task
def clean(c):
    """Removes all test, build, log and lint artifacts from the environment."""
    _clean_mypy()
    _clean_build()
    _clean_python()
    _clean_test()
    _clean_docs()
    _clean_flake8()


@task(
    name="lint-isort",
    aliases=[
        "isort",
        "is",
    ],
    help={
        "check": "Checks if source is formatted without applying changes",
        "all-files": "Selects all files to be scanned. Default is 'src' only",
    },
)
def lint_isort(c, check=False, all_files=False):
    """Run isort against selected python files."""
    isort_options = ["--check-only", "--diff"] if check else []
    if all_files:
        # noinspection PyCompatibility
        c.run(f"isort {' '.join(isort_options)} {PYTHON_FILES_ALL_STR}")
    else:
        # noinspection PyCompatibility
        c.run(f"isort {' '.join(isort_options)} {PYTHON_FILES_SRC_STR}")


@task(
    name="lint-black",
    aliases=[
        "black",
        "bl",
    ],
    help={
        "check": "Checks if source is formatted without applying changes",
        "all-files": "Selects all files to be scanned. Default is 'src' only",
    },
    optional=["all_files"],
)
def lint_black(c, check=False, all_files=False):
    """Runs black formatter against selected python files."""
    black_options = ["--diff", "--check"] if check else []
    if all_files:
        # noinspection PyCompatibility
        c.run(f"black {' '.join(black_options)} {PYTHON_FILES_ALL_STR}")
    else:
        # noinspection PyCompatibility
        c.run(f"black {' '.join(black_options)} {PYTHON_FILES_SRC_STR}")


@task(
    name="lint-flake8",
    aliases=[
        "flake8",
        "fl",
    ],
    help={
        "all-files": "Selects all files to be scanned. Default is 'src' only",
    },
    optional=["all_files"],
)
def lint_flake8(c, all_files=False):
    """Run flake8 against selected files."""
    _clean_flake8()
    if all_files:
        # noinspection PyCompatibility
        c.run(f"flake8 {PYTHON_FILES_ALL_STR} --max-line-length=100")
    else:
        # noinspection PyCompatibility
        c.run(f"flake8 {PYTHON_FILES_SRC_STR} tests --max-line-length=100")


@task(pre=[lint_isort, lint_black, lint_flake8])
def lint(c):
    """Run all lint tasks on 'src' files only."""


# noinspection PyTypeChecker
@task(
    pre=[
        call(lint_isort, all_files=True),
        call(lint_black, all_files=True),
        call(lint_flake8, all_files=True),
    ]
)
def lint_all(c):
    """Run all lint tasks on all files."""


@task(
    help={
        "open_browser": "Open the mypy report in the web browser",
        "all-files": "Selects all files to be scanned. Default is 'src' only",
    },
)
def mypy(c, open_browser=False, all_files=False):
    """Run mypy against selected python files."""
    _clean_mypy()
    if all_files:
        # noinspection PyCompatibility
        c.run(f"mypy {PYTHON_FILES_ALL_STR}")
    else:
        # noinspection PyCompatibility
        c.run(f"mypy {PYTHON_FILES_SRC_STR}")
    if open_browser:
        report_path = '"' + str(ROOT_DIR / "mypy-report" / "index.html") + '"'
        webbrowser.open(report_path)


@task
def test(c):
    """Run tests using pytest."""
    _clean_test()
    c.run("tox")


@task(
    help={
        "open_browser": "Open the docs in the web browser",
    },
)
def docs(c, open_browser=False):
    """Build documentation."""
    _clean_docs()
    # noinspection PyCompatibility
    build_docs = f'sphinx-build -b html "{DOC_DIR}" "{DOCS_BUILD_DIR}"'
    c.run(build_docs)
    if open_browser:
        webbrowser.open(str(DOCS_INDEX))


@task
def build(c):
    """Creates a new sdist & wheel build using the PyPA tool."""
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


@task
def psr(c):
    """Runs semantic-release publish."""
    _clean_build()
    c.run("semantic-release publish")


@task
def update(c):
    """Updates the development environment"""
    c.run("pre-commit clean")
    c.run("pre-commit gc")
    c.run("pre-commit autoupdate")
