"""
uPyTest (MicroPyTest)

A small and *very limited* module for very simple PyTest inspired tests to run
in the MicroPython runtime within PyScript.

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
"""

import sys
import os
import io
import inspect
import time
from pathlib import Path


__all__ = [
    "discover",
    "raises",
    "skip",
    "run",
]


#: To contain references to any skipped tests.
_SKIPPED_TESTS = []


# Possible states for a test case.
#: The test is yet to run.
PENDING = "pending"
#: The test was successful.
PASS = "pass"
#: The test did not pass.
FAIL = "fail"
#: The test was skipped.
SKIPPED = "skipped"


def is_awaitable(obj):
    """
    Returns a boolean indication if the passed in obj is an awaitable
    function. (MicroPython treats awaitables as generator functions.)
    """
    return inspect.isgeneratorfunction(obj)


class TestCase:
    """
    Represents an individual test to run.
    """

    def __init__(self, test_function, module_name, test_name):
        """
        A TestCase is instantiated with a callable test_function, the name of 
        the module containing the test, and the name of the test within the
        module.
        """
        self.test_function = test_function
        self.module_name = module_name
        self.test_name = test_name
        self.status = PENDING  # the initial state of the test.
        self.traceback = None  # to contain details of any failure.

    async def run(self):
        """
        Run the test function and set the status and traceback attributes, as
        required.
        """
        if self.test_function in _SKIPPED_TESTS:
            self.status = SKIPPED
            return
        try:
            if is_awaitable(self.test_function):
                await self.test_function()
            else:
                self.test_function()
            self.status = PASS
        except Exception as ex:
            self.status = FAIL
            # Gather a traceback from the caught exception.
            traceback_data = io.StringIO()
            sys.print_exception(ex, traceback_data)
            traceback_data.seek(0)
            self.traceback = traceback_data.read()


class TestModule:
    """
    Represents a module containing tests.
    """

    def __init__(self, path, module_name, module, setup=None, teardown=None):
        """
        A TestModule is instantiated with a path to its location on the
        filesystem, the name of the module, and an object representing the 
        Python module itself.

        Optional global setup and teardown callables may also be supplied. If 
        the module already contains valid setup/teardown functions, these will 
        be used instead.
        """
        self.path = path
        self.module_name = module_name
        self.module = module
        self._setup = setup
        self._teardown = teardown
        self._tests = []
        # Harvest references to test functions, setup and teardown.
        for name, item in self.module.__dict__.items():
            if callable(item) or is_awaitable(item):
                if name.startswith("test"):
                    t = TestCase(item, self.path, name)
                    self._tests.append(t)
                elif name == "setup":
                    self._setup = item
                elif name == "teardown":
                    self._teardown = item

    @property
    def tests(self):
        """
        Return a list containing TestCase instances drawn from the
        content of the test module.
        """
        return self._tests

    @property
    def setup(self):
        """
        Get the setup function for the module.
        """
        return self._setup

    @property
    def teardown(self):
        """
        Get the teardown function for the module.
        """
        return self._teardown

    async def run(self):
        """
        Run each TestCase instance for this module. If a setup or teardown
        exists, these will be evaluated immediately before and after the
        TestCase is run. 
        
        Print a dot for each passing test, an F for each failing test, and an S
        for each skipped test.
        """
        for test_case in self.tests:
            if self.setup:
                if is_awaitable(self.setup):
                    await self.setup()
                else:
                    self.setup()
            await test_case.run()
            if self.teardown:
                if is_awaitable(self.teardown):
                    await self.teardown()
                else:
                    self.teardown()
            if test_case.status == SKIPPED:
                print("S", end="")
            elif test_case.status == PASS:
                print(".", end="")
            else:
                print("F", end="")


def discover(start_dir, pattern, setup=None, teardown=None):
    """
    Return a list of TestModule instances representing Python modules
    recursively found in the start_dir and whose name matches the pattern for
    identifying test modules. 
    
    If global setup and teardown functions are provided, these will be used for
    each test module unless overridden by module-specific setup and teardown 
    functions.
    """
    result = []
    for module_match in Path(start_dir).rglob(pattern):
        full_path = module_match
        module_dir, module_file = os.path.split(full_path)
        module_name, _module_ext = module_file.rsplit(".", 1)
        cwd = os.path.abspath(os.getcwd())
        os.chdir(module_dir)
        module_instance = __import__(module_name)
        os.chdir(cwd)
        module = TestModule(
            full_path, module_name, module_instance, setup, teardown
        )
        result.append(module)
    return result


class raises:
    """
    A context manager to ensure expected exceptions are raised.
    """

    def __init__(self, *expected_exceptions):
        """
        Pass in expected exception classes that should be raised within the
        scope of the context manager.
        """
        if not expected_exceptions:
            raise ValueError("Missing expected exceptions.")
        # Check the args are all children of BaseException.
        for ex in expected_exceptions:
            if not issubclass(ex, BaseException):
                raise TypeError(f"{ex} is not an Exception.")
        self.expected_exceptions = expected_exceptions
        self.exception = None
        self.traceback = None

    def __enter__(self):
        return self  # Return self to the context for "as" clauses.

    def __exit__(self, ex_type, ex_value, ex_tb):
        # Check the exception type.
        if ex_type not in self.expected_exceptions:
            # No such expected exception, so raise AssertionError with a
            # helpful message.
            message = "Did not raise expected exception."
            expected = ", ".join(
                [str(ex.__name__) for ex in self.expected_exceptions]
            )
            if ex_type:
                message += f" Expected {expected}; but got {ex_type.__name__}."
            else:
                message += f" Expected {expected}; but got None."
            raise AssertionError(message)
        self.exception = ex_value
        self.traceback = ex_tb
        return True  # Suppress the expected exception.


def skip(reason=""):
    """
    A decorator to indicate the decorated test function should be skipped
    (with optional reason).
    """

    def decorator(func):
        global _SKIPPED_TESTS
        _SKIPPED_TESTS.append(func)
        return func

    return decorator


async def run(start_dir=".", pattern="test_*.py"):
    """
    Run the test suite given a start_dir and pattern for identifying test
    modules. 
    
    If there is a conftest.py file in the start_dir, it will be imported for
    any global setup and teardown functions to use. These setup and teardown
    functions can be overridden in the individual test modules.
    """
    setup = None
    teardown = None
    conftest = Path(start_dir) / "conftest.py"
    if os.path.exists(str(conftest)):
        print("Using conftest.py for global setup and teardown.")
        cwd = os.path.abspath(os.getcwd())
        os.chdir(os.path.abspath(start_dir))
        conftest_instance = __import__(conftest.stem)
        os.chdir(cwd)
        setup = (
            conftest_instance.setup
            if hasattr(conftest_instance, "setup")
            else None
        )
        teardown = (
            conftest_instance.teardown
            if hasattr(conftest_instance, "teardown")
            else None
        )
    test_modules = discover(start_dir, pattern, setup, teardown)
    module_count = len(test_modules)
    test_count = sum([len(module.tests) for module in test_modules])
    print(
        f"Found {module_count} test module[s]. Running {test_count} test[s].\n"
    )

    failed_tests = []
    skipped_tests = []
    start = time.time()
    for module in test_modules:
        await module.run()
        for test in module.tests:
            if test.status == FAIL:
                failed_tests.append(test)
            elif test.status == SKIPPED:
                skipped_tests.append(test)
    end = time.time()
    print("")
    if failed_tests:
        print(
            "================================= FAILURES ================================="
        )
        for failed in failed_tests:
            print("")
            print(failed.module_name, "::", failed.test_name, sep="")
            print(failed.traceback)
    error_count = len(failed_tests)
    skip_count = len(skipped_tests)
    pass_count = test_count - error_count - skip_count
    dur = end - start
    print(
        "========================= short test summary info =========================="
    )
    print(
        f"{error_count} failed, {skip_count} skipped, {pass_count} passed in {dur:.2f} seconds"
    )
