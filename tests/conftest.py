from pyscript import window


def setup():
    window.console.log("Setup from conftest.py")


def teardown():
    window.console.log("Teardown from conftest.py")
