"""
A test module that will just use global setup and teardown functions. (Check
the browser console for the output of the setup and teardown functions.)
"""

import upytest
import asyncio


@upytest.skip("This test will be skipped")
def test_skipped():
    """
    Test functions decorated with `@upytest.skip` will be skipped.
    """
    assert False  # This will not be executed.


def test_passes():
    """
    A test function that passes with a true assertion.
    """
    assert True, "This test passes"


def test_fails():
    """
    A test function that fails with a false assertion.
    """
    assert False, "This test fails"


def test_raises_expects_base_exception_children():
    """
    Check that `upytest.raises` expects subclasses of `BaseException`.
    """
    # Must have expected exception[s] as arguments.
    with upytest.raises(ValueError):
        with upytest.raises():
            pass
    # Expected exception must be a subclass of BaseException.
    with upytest.raises(TypeError):
        with upytest.raises("not a BaseException"):
            pass


def test_raises_exception():
    """
    Test that the expected exception is raised, and so the test will pass.
    """
    with upytest.raises(ValueError):
        raise ValueError("This is a ValueError")


def test_does_not_raise_exception():
    """
    Test that the expected exception is not raised. This test will fail.
    """
    with upytest.raises(ValueError):
        pass


def test_does_not_raise_expected_exception():
    """
    Test when the wrong exception is raised. This test will fail.
    """
    with upytest.raises(ValueError, AssertionError):
        raise TypeError("This is a TypeError")


# Async versions of the above.


@upytest.skip("This async test will be skipped")
async def test_async_skip():
    assert False  # This will not be executed.


async def test_async_passes():
    await asyncio.sleep(0.2)
    assert True, "This async test passes."


async def test_async_fails():
    await asyncio.sleep(0.2)
    assert False, "This async test fails."


async def test_async_raises_exception():
    await asyncio.sleep(0.2)
    with upytest.raises(ValueError):
        raise ValueError("This is a ValueError")


async def test_async_does_not_raise_exception():
    await asyncio.sleep(0.2)
    with upytest.raises(ValueError):
        pass


async def test_async_does_not_raise_expected_exception():
    await asyncio.sleep(0.2)
    with upytest.raises(ValueError, AssertionError):
        raise TypeError("This is a TypeError")
