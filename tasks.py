from invoke import task


TEST_FOLDER = "tests"


@task
def clean_cache(c):
    print("Cleaning module cache.")
    c.run("rm -rf .pytest_cache")


@task
def clean_test_cache(c):
    print("Cleaning test cache.")
    c.run("rm -rf {}/resources/Arma".format(TEST_FOLDER))
    c.run("rm -rf {}/.pytest_cache".format(TEST_FOLDER))


@task(pre=[clean_cache, clean_test_cache])
def clean(c):
    pass


@task
def test(c):
    c.run("pipenv run pytest -s {}".format(TEST_FOLDER))


@task
def test_this(c):
    c.run("pipenv run pytest -s -p no:sugar -m \"runthis\" {}".format(TEST_FOLDER))
