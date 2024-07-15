"""
Tests in this module will use only the local setup and teardown functions. (See
the browser console for the output of the setup and teardown functions.)
"""
import upytest
import asyncio
from pyscript import window


async def setup():
    window.console.log("Setup from async setup function in module")


async def teardown():
    window.console.log("Teardown from async teardown function in module")


def test_with_local_setup_teardown():
    """
    A test function that will use the local setup and teardown functions.
    """
    assert True, "This test passes"
    window.console.log("Test function with local setup and teardown")