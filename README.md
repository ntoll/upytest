# uPyTest (MicroPytest) 🔬🐍✔️

A small and very limited module for very simple [PyTest](https://pytest.org) 
inspired tests to run in the [MicroPython](https://micropython.org/) runtime
within [PyScript](https://pyscript.net/). 

It currently only implements naive versions of:

* Discovery of tests on the filesystem.
* `assert` statements for testing state.
* `assert <something>, "Some description"` to add contextual information.
* Global `setup` and `teardown` functions via `conftest.py`.
* Module specific `setup` and `teardown` functions.
* A `skip("reason")` decorator for skipping test functions.
* Checks for expected exceptions via a `raises` context manager.
* Synchronous and asynchronous test cases.

## Usage

**This module is for use with MicroPython within PyScript.**

### Setup

1. Ensure the `upytest.py` file is in your Python path. You may need to copy
   this over using the 
   [files settings](https://docs.pyscript.net/2024.7.1/user-guide/configuration/#files). 
   (See the `config.json` file in this repository for an example of this in 
   action.)
2. Create and copy over your tests. Once again use the files settings, and the
   `config.json` in this repository demonstrates how to copy over the content
   of the `tests` directory found in this repository.
3. In your `main.py` (or whatever you call your main Python script), simply
   import upytest and await the `run` method while passing in the test 
   directory:
   ```python
   import upytest

   await upytest.run("./tests")
   ```
   (This is demonstrated in the `main.py` file in this repository.)
4. In your `index.html` make sure you use the `async` and `terminal` attributes
   when referencing your MicroPython script (as in the `index.html` file in
   this repository):
   ```html
   <script type="mpy" src="./main.py" config="./config.json" terminal async></script>
   ```

Simply point your browser at your `index.html` and your should see the test
suite run.

### Writing tests

**`upytest` is only _inspired by PyTest_ and is not intended as a replacement.**

Some of the core concepts and capabilities used in `upytest` will be familiar 
from using PyTest, but the specific API, capabilities and implementation details
will be very different.

To create a test suite ensure your test functions are contained in modules
inside your test directory that start with `test_`. If you want to change this
pattern for matching test modules pass in a `pattern` argument as a string to
the `upytest.run` method (whose default is currently `pattern="test*.py"`).

Inside the test module, test functions are identified by having `test_`
prepended to their name:

```python
def test_something():
    assert True, "This will not fail."
```

Just like PyTest, use the `assert` statement to verify test expectations. As
shown above, a string following a comma is used as the value for any resulting
`AssertionError` should the `assert` fail.

Sometimes you need to skip existing tests. Simply use the `skip` decorator like
this:

```python
import upytest


@upytest.skip("This is my reason for skipping the test")
def test_skipped():
    assert False, "This won't fail, because it's skipped!"
```

Often you need to check a certain exception is raised when a problematic state
is achieved. To do this use the `raises` context manager like this:

```python
import upytest


def test_raises_exception():
    with upytest.raises(ValueError, KeyError):
        raise ValueError("BOOM!")
```

The `raises` context manager requires one or more expected exceptions that
should be raised while the code within its context is evaluated. If no such
exceptions are raised, the test fails.

Sometimes you need to perform tasks either before or after a number of tests
are run. For example, they might be needed to create a certain state, or clean
up and reset after tests are run. These tasks are achieved by two functions
called `setup` (run immediately before tests) and `teardown` (run immediately 
after tests).

These functions are entirely optional and should be defined in two possible
places:

* In a `conftest.py` file in the root of your test directory. Any `setup` or
  `teardown` function defined here will be _applied to all tests_.
* In individual test modules. The `setup` and `teardown` functions in test
  modules _replace any global versions of these functions defined in 
  conftest.py_. They only apply to test functions found within the module in
  which they are defined. If you still need to run the global functions, just 
  import them and call them from within your test module versions.

All test functions along with `setup` and `teardown` can be awaitable /
asynchronous. 

All these features are demonstrated within the test modules in the `tests`
directory of this project.

### Test output

Test output tries to be informative, indicating the time taken, the number of
tests, the number of pass, fails and skips along with tracebacks for failures.

When outputting a test run a `.` represents a passing test, an `F` a failure
and `S` a skipped test.

The output for the test suite for this module is a good example of all the
different sorts of information you may see:

```
Using conftest.py for global setup and teardown.
Found 2 test module[s]. Running 22 test[s].

F.FF.SFF..FF.FS.FF..FF
================================= FAILURES =================================

./tests/test_with_setup_teardown.py::test_async_fails
Traceback (most recent call last):
  File "upytest.py", line 89, in run
  File "test_with_setup_teardown.py", line 51, in test_async_fails
AssertionError: This async test fails.


./tests/test_with_setup_teardown.py::test_async_does_not_raise_exception
Traceback (most recent call last):
  File "upytest.py", line 89, in run
  File "test_with_setup_teardown.py", line 61, in test_async_does_not_raise_exception
  File "upytest.py", line 238, in __exit__
AssertionError: Did not raise expected exception. Expected ValueError; but got None.


./tests/test_with_setup_teardown.py::test_async_does_not_raise_expected_exception
Traceback (most recent call last):
  File "upytest.py", line 89, in run
  File "test_with_setup_teardown.py", line 66, in test_async_does_not_raise_expected_exception
  File "upytest.py", line 238, in __exit__
AssertionError: Did not raise expected exception. Expected ValueError, AssertionError; but got 
TypeError.


./tests/test_with_setup_teardown.py::test_does_not_raise_exception
Traceback (most recent call last):
  File "upytest.py", line 91, in run
  File "test_with_setup_teardown.py", line 33, in test_does_not_raise_exception
  File "upytest.py", line 238, in __exit__
AssertionError: Did not raise expected exception. Expected ValueError; but got None.


./tests/test_with_setup_teardown.py::test_does_not_raise_expected_exception
Traceback (most recent call last):
  File "upytest.py", line 91, in run
  File "test_with_setup_teardown.py", line 38, in test_does_not_raise_expected_exception
  File "upytest.py", line 238, in __exit__
AssertionError: Did not raise expected exception. Expected ValueError, AssertionError; but got 
TypeError.


./tests/test_with_setup_teardown.py::test_fails
Traceback (most recent call last):
  File "upytest.py", line 91, in run
  File "test_with_setup_teardown.py", line 23, in test_fails
AssertionError: This test fails.


./tests/test_stuff.py::test_async_does_not_raise_expected_exception
Traceback (most recent call last):
  File "upytest.py", line 89, in run
  File "test_stuff.py", line 57, in test_async_does_not_raise_expected_exception
  File "upytest.py", line 238, in __exit__
AssertionError: Did not raise expected exception. Expected ValueError, AssertionError; but got 
TypeError.


./tests/test_stuff.py::test_async_fails
Traceback (most recent call last):
  File "upytest.py", line 89, in run
  File "test_stuff.py", line 42, in test_async_fails
AssertionError: This async test fails.


./tests/test_stuff.py::test_does_not_raise_exception
Traceback (most recent call last):
  File "upytest.py", line 91, in run
  File "test_stuff.py", line 24, in test_does_not_raise_exception
  File "upytest.py", line 238, in __exit__
AssertionError: Did not raise expected exception. Expected ValueError; but got None.


./tests/test_stuff.py::test_does_not_raise_expected_exception
Traceback (most recent call last):
  File "upytest.py", line 91, in run
  File "test_stuff.py", line 29, in test_does_not_raise_expected_exception
  File "upytest.py", line 238, in __exit__
AssertionError: Did not raise expected exception. Expected ValueError, AssertionError; but got 
TypeError.


./tests/test_stuff.py::test_async_does_not_raise_exception
Traceback (most recent call last):
  File "upytest.py", line 89, in run
  File "test_stuff.py", line 52, in test_async_does_not_raise_exception
  File "upytest.py", line 238, in __exit__
AssertionError: Did not raise expected exception. Expected ValueError; but got None.


./tests/test_stuff.py::test_fails
Traceback (most recent call last):
  File "upytest.py", line 91, in run
  File "test_stuff.py", line 14, in test_fails
AssertionError: This test fails

========================= short test summary info ==========================
12 failed, 2 skipped, 8 passed in 0.01 seconds
```

## Developer setup

This is easy:

1. Clone the project.
2. Start a local web server: `python -m http.server`
3. Point your browser at http://localhost:8000/
4. Change code and refresh your browser to check your changes.
5. **DO NOT CREATE A NEW FEATURE WITHOUT FIRST CREATING AN ISSUE FOR IT IN WHICH
   YOU PROPOSE YOUR CHANGE**. (We want to avoid a situation where you work hard
   on something that is ultimately rejected by the maintainers.)
6. Given all the above, pull requests are welcome and greatly appreciated.

We expect all contributors to abide by the spirit of our
[code of conduct](./CODE_OF_CONDUCT.md).

## Testing uPyTest

See the content of the `tests` directory in this repository. To run the test
suite, just follow steps 1, 2 and 3 in the developer setup section.

## License

Copyright (c) 2024 Nicholas H.Tollervey

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.