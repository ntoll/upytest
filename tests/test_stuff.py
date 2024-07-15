import upytest


@upytest.skip("This test will be skipped")
def test_skipped():
    assert False  # This will not be executed.


def test_passes():
    assert True, "This test passes"


def test_fails():
    assert False, "This test fails"


def test_raises_exception():
    with upytest.raises(ValueError):
        raise ValueError("This is a ValueError")


def test_does_not_raise_exception():
    with upytest.raises(ValueError):
        pass


@upytest.skip("This async test will be skipped")
async def test_async_passes():
    assert False  # This will not be executed.


async def test_async_passes():
    assert True, "This async test passes."


async def test_async_fails():
    assert False, "This async test fails."


async def test_async_raises_exception():
    with upytest.raises(ValueError):
        raise ValueError("This is a ValueError")


async def test_async_does_not_raise_exception():
    with upytest.raises(ValueError):
        pass
