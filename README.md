# uPyTest (MicroPytest) 🔬🐍✔️

A small and very limited module for very simple [PyTest](https://pytest.org) 
inspired tests to run in the [MicroPython](https://micropython.org/) and
[Pyodide](https://pyodide.org/) interpreters within 
[PyScript](https://pyscript.net/). 

It currently only implements naive versions of:

* Discovery of tests on the filesystem.
* `assert` statements for testing state.
* `assert <something>, "Some description"` to add contextual information.
* Global `setup` and `teardown` functions via `conftest.py`.
* Module specific `setup` and `teardown` functions.
* A `skip("reason")` decorator for skipping test functions.
* Checks for expected exceptions via a `raises` context manager.
* Synchronous and asynchronous test cases.
* Works well with [uMock](https://github.com/ntoll/umock).

There are two major reasons this project exists:

1. MicroPython doesn't have a test framework like PyTest, and folks want to
   test PyScript code running in MicroPython.
2. Using the same test framework with both MicroPython and Pyodide will ensure
   the test suite can exercise your code running on both interpreters (and
   perhaps highlight places where behaviour differs).

Of course, **you should write tests for your code**! If only because it means
you'll be able to make changes in the future with confidence. The aim of
`upytest` is to make this is simple as possible, in a way that is familiar to
those who use PyTest, when using PyScript.

## Usage

**This module is for use within PyScript.**

### Setup / Run tests

1. Ensure the `upytest.py` file is in your Python path. You may need to copy
   this over using the 
   [files settings](https://docs.pyscript.net/2024.8.2/user-guide/configuration/#files). 
   (See the `config.json` file in this repository for an example of this in 
   action.)
2. Create and copy over your tests. Once again use the files settings, and the
   `config.json` in this repository demonstrates how to copy over the content
   of the `tests` directory found in this repository.
3. In your `main.py` (or whatever you call your Python script for starting the
   tests), simply `import upytest` and await the `run` method while passing in
   one or more strings indicating the tests to run:
   ```python
   import upytest


   results = await upytest.run("./tests")
   ```
   (This is demonstrated in the `main.py` file in this repository.)
4. The specification may be simply a string describing the directory in
   which to start looking for test modules (e.g. `"./tests"`), or strings
   representing the names of specific test modules / tests to run (of the
   form: "module_path" or "module_path::test_function"; e.g.
   `"tests/test_module.py"` or `"tests/test_module.py::test_stuff"`).
5. If a named `pattern` argument is provided, it will be used to match test
   modules in the specification for target directories. The default pattern is
   "test_*.py".
6. If there is a `conftest.py` file in any of the specified directories
   containing a test module, it will be imported for any global `setup` and
   `teardown` functions to use for modules found within that directory. These
   `setup` and `teardown` functions can be overridden in the individual test
   modules.
7. The `result` of awaiting `upytest.run` is a Python dictionary containing 
  lists of tests bucketed under the keys: `"passes"`, `"fails"` and 
  `"skipped"`. These results can be used for further processing and analysis
  (again, see `main.py` for an example of this in action.)
8. In your `index.html` make sure you use the `terminal` attribute
   when referencing your Python script (as in the `index.html` file in
   this repository):
   ```html
   <script type="mpy" src="./main.py" config="./config.json" terminal></script>
   ```
   You should be able to use the `type` attribute of `"mpy"` (for MicroPython)
   and `"py"` (for Pyodide) interchangeably.

Finally, point your browser at your `index.html` and your should see the test
suite run.

### Writing tests

**`upytest` is only _inspired by PyTest_ and is not intended as a replacement.**

Some of the core concepts and capabilities used in `upytest` will be familiar 
from using PyTest, but the specific API, capabilities and implementation
details _will be very different_.

To create a test suite ensure your test functions are contained in modules,
whose names start with `test_`, found inside your `test` directory. If you want
to change this pattern for matching test modules pass in a `pattern` argument
as a string to the `upytest.run` method (whose default is currently
`pattern="test*.py"`).

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
  `teardown` function defined here will be _applied to all tests_, unless
  you override these functions...
* In individual test modules. The `setup` and `teardown` functions in test
  modules _replace any global versions of these functions defined in 
  conftest.py_. They only apply to _test functions found within the module_ in
  which they are defined. If you still need to run the global functions, just 
  import them and call them from within your test module versions.

All test functions along with `setup` and `teardown` can be awaitable /
asynchronous.

All these features are demonstrated within the test modules in the `tests`
directory of this project.

### Test output

Test output tries to be informative, indicating the time taken, the number of
tests, the number of passes, fails and skips along with tracebacks for
failures.

Due to the small nature of MicroPython, the information from the traceback for
failing tests may not appear as comprehensive as the information you may be
used to see after a run of classic PyTest. Nevertheless, line numbers and the
call stack are included to provide you with enough information to see what has
failed, and where.

When outputting a test run a `.` represents a passing test, an `F` a failure
and `S` a skipped test.

The output for the test suite for this module is a good example of all the
different sorts of information you may see:

```
Using ./tests/conftest.py for global setup and teardown in ./tests.
Using local setup and teardown for ./tests/test_with_setup_teardown.py.
Found 2 test module[s]. Running 14 test[s].

..FF..SFF.SFF.
================================= FAILURES =================================
Failed: ./tests/test_core_functionality.py::test_does_not_raise_expected_exception_fails
Traceback (most recent call last):
  File "upytest.py", line 143, in run
  File "tests/test_core_functionality.py", line 67, in test_does_not_raise_expected_exception_fails
AssertionError: Did not raise expected exception. Expected ValueError, AssertionError; but got TypeError.


Failed: ./tests/test_core_functionality.py::test_async_does_not_raise_expected_exception_fails
Traceback (most recent call last):
  File "upytest.py", line 141, in run
  File "tests/test_core_functionality.py", line 98, in test_async_does_not_raise_expected_exception_fails
AssertionError: Did not raise expected exception. Expected ValueError, AssertionError; but got TypeError.


Failed: ./tests/test_core_functionality.py::test_does_not_raise_exception_fails
Traceback (most recent call last):
  File "upytest.py", line 143, in run
  File "tests/test_core_functionality.py", line 59, in test_does_not_raise_exception_fails
AssertionError: Did not raise expected exception. Expected ValueError; but got None.


Failed: ./tests/test_core_functionality.py::test_async_fails
Traceback (most recent call last):
  File "upytest.py", line 141, in run
  File "tests/test_core_functionality.py", line 83, in test_async_fails
AssertionError: This async test fails.


Failed: ./tests/test_core_functionality.py::test_async_does_not_raise_exception_fails
Traceback (most recent call last):
  File "upytest.py", line 141, in run
  File "tests/test_core_functionality.py", line 93, in test_async_does_not_raise_exception_fails
AssertionError: Did not raise expected exception. Expected ValueError; but got None.


Failed: ./tests/test_core_functionality.py::test_fails
Traceback (most recent call last):
  File "upytest.py", line 143, in run
  File "tests/test_core_functionality.py", line 28, in test_fails
AssertionError: This test will fail

========================= short test summary info ==========================
6 failed, 2 skipped, 6 passed in 0.00 seconds
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
suite, just follow steps 1, 2 and 3 in the developer setup section. The
`main.py` script tests the test framework itself. From the docstring for that
module:

> How do you test a test framework?
>
> You can't use the test framework to test itself, because it may contain bugs!
> Hence this script, which uses upytest to run tests and check the results are as
> expected. The expected results are hard-coded in this script, and the actual
> results are generated by running tests with upytest. The script then compares
> the expected and actual results to ensure they match.
>
> Finally, the script creates a div element to display the results in the page.
> If tests fail, the script will raise an AssertionError, which will be
> displayed with a red background. If the tests pass, the script will display a
> message with a green background.
>
> There are two sorts of expected results: the number of tests that pass, fail,
> and are skipped, and the names of the tests that pass, fail, and are skipped.
> Tests that pass end with "passes", tests that fail end with "fails", and tests
> that are skipped end with "skipped".
>
> This script will work with both MicroPython and Pyodide, just so we can ensure
> the test framework works in both environments. The index.html file uses
> MicroPython, the index2.html file uses Pyodide.
>
> That's it! Now we can test a test framework with a meta-test framework. 🤯

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