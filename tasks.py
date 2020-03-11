from invoke import task


TEST_FOLDER = "tests"
TEST_COVERAGE_HTML_FOLDER = "tests_coverage"


@task
def clean_cache(c):
    print("Cleaning module cache.")
    c.run("rm -rf .pytest_cache")


@task
def clean_test_cache(c):
    print("Cleaning test cache.")
    c.run("rm -rf {}/resources/Arma".format(TEST_FOLDER))
    c.run("rm -rf {}/.pytest_cache".format(TEST_FOLDER))


@task
def clean_coverage_html(c):
    print("Cleaning test coverage html data.")
    c.run("rm -rf {}".format(TEST_COVERAGE_HTML_FOLDER))


@task(pre=[clean_cache, clean_test_cache, clean_coverage_html])
def clean(c):
    pass


@task
def test_cov(c, s=False, h=False):
    s_string = " -s " if s else " "
    h_string = "--cov-report html:{} ".format(TEST_COVERAGE_HTML_FOLDER) if h else ""
    c.run("pipenv run pytest {}--cov-report term-missing:skip-covered "
          "--cov=odk_servermanager {}{}".format(h_string, s_string, TEST_FOLDER))


@task
def test(c, s=False):
    s_string = " -s " if s else " "
    c.run("pipenv run pytest{}{}".format(s_string, TEST_FOLDER))


@task
def test_this(c):
    c.run("pipenv run pytest -s -p no:sugar -m \"runthis\" {}".format(TEST_FOLDER))
