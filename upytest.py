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

try:
    # Pyodide.
    from traceback import print_exception
except ImportError:
    # MicroPython
    from sys import print_exception


__all__ = [
    "discover",
    "raises",
    "skip",
    "run",
]


#: A flag to show if MicroPython is the current Python interpreter.
is_micropython = "micropython" in sys.version.lower()


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
    if is_micropython:
        return inspect.isgeneratorfunction(obj)
    return inspect.iscoroutinefunction(obj)


def import_module(module_path):
    """
    Import a module from a given file path, in a way that works with both
    MicroPython and Pyodide.
    """
    dotted_path = str(module_path).replace("/", ".").replace(".py", "")
    dotted_path = dotted_path.lstrip(".")
    module = __import__(dotted_path)
    for part in dotted_path.split(".")[1:]:
        module = getattr(module, part)
    return module


def parse_traceback_from_exception(ex):
    """
    Parse the traceback from an exception object.
    """
    traceback_data = io.StringIO()
    if is_micropython:
        print_exception(ex, traceback_data)
    else:
        print_exception(ex, file=traceback_data)
    traceback_data.seek(0)
    raw_traceback = traceback_data.read()
    # Ensure removal of any __exit__ related lines caused by the raises context
    # manager and MicroPython.
    result = []
    for line in raw_traceback.split("\n"):
        if line.endswith("in __exit__") and "upytest" in line:
            continue
        result.append(line)
    return "\n".join(result)


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
            self.traceback = parse_traceback_from_exception(ex)


class TestModule:
    """
    Represents a module containing tests.
    """

    def __init__(self, path, module, setup=None, teardown=None):
        """
        A TestModule is instantiated with a path to its location on the
        filesystem and an object representing the Python module itself.

        Optional global setup and teardown callables may also be supplied. If
        the module already contains valid setup/teardown functions, these will
        be used instead.
        """
        self.path = path
        self.module = module
        self._setup = setup
        self._teardown = teardown
        self._tests = []
        local_setup_teardown = False
        # Harvest references to test functions, setup and teardown.
        for name, item in self.module.__dict__.items():
            if callable(item) or is_awaitable(item):
                if name.startswith("test"):
                    t = TestCase(item, self.path, name)
                    self._tests.append(t)
                elif name == "setup":
                    self._setup = item
                    local_setup_teardown = True
                elif name == "teardown":
                    self._teardown = item
                    local_setup_teardown = True
        if local_setup_teardown:
            print(
                f"Using \033[1mlocal\033[0m setup and teardown for \033[1m{self.path}\033[0m."
            )

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

    def limit_tests_to(self, test_names):
        """
        Limit the tests run to the provided test_names list of names.
        """
        self._tests = [t for t in self._tests if t.test_name in test_names]

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
                print("\033[33;1mS\033[0m", end="")
            elif test_case.status == PASS:
                print("\033[32;1m.\033[0m", end="")
            else:
                print("\033[31;1mF\033[0m", end="")


def gather_conftest_functions(conftest_path, target):
    """
    Import the conftest.py module from the given Path instance, and return the
    global setup and teardown functions for the target (if they exist).
    """
    conftest_path = str(conftest_path)
    if os.path.exists(conftest_path):
        print(
            f"Using \033[1m{conftest_path}\033[0m for global setup and teardown in \033[1m{target}\033[0m."
        )
        conftest = import_module(conftest_path)
        setup = conftest.setup if hasattr(conftest, "setup") else None
        teardown = conftest.teardown if hasattr(conftest, "teardown") else None
        return setup, teardown
    return None, None


def discover(targets, pattern, setup=None, teardown=None):
    """
    Return a list of TestModule instances representing Python modules
    recursively found via the targets and, if a target is a directory, whose
    module name matches the pattern for identifying test modules.

    The targets may be simply a string describing the directory in
    which to start looking for test modules (e.g. "./tests"), or strings
    representing the names of specific test modules / tests to run (of the
    form: "module_path" or "module_path::test_function" or
    "module_path::test_function_1,test_function_2"; e.g. "tests/test_module.py"
    or "tests/test_module.py::test_stuff" or
    "tests/test_module.py::test_stuff,test_more_stuff").

    If there is a conftest.py file in any of the specified directories
    containing a test module, it will be imported for any global setup and
    teardown functions to use for modules found within that directory. These
    setup and teardown functions can be overridden in the individual test
    modules.
    """
    result = []
    for target in targets:
        if "::" in target:
            conftest_path = Path(target.split("::")[0]).parent / "conftest.py"
            setup, teardown = gather_conftest_functions(conftest_path, target)
            module_path, test_names = target.split("::")
            module_instance = import_module(module_path)
            module = TestModule(module_path, module_instance, setup, teardown)
            module.limit_tests_to(test_names.split(","))
            result.append(module)
        elif os.path.isdir(target):
            conftest_path = Path(target) / "conftest.py"
            setup, teardown = gather_conftest_functions(conftest_path, target)
            for module_path in Path(target).rglob(pattern):
                module_instance = import_module(module_path)
                module = TestModule(
                    module_path, module_instance, setup, teardown
                )
                result.append(module)
        else:
            conftest_path = Path(target).parent / "conftest.py"
            setup, teardown = gather_conftest_functions(conftest_path, target)
            module_instance = import_module(target)
            module = TestModule(target, module_instance, setup, teardown)
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


def skip(reason="", when=True):
    """
    A decorator to indicate the decorated test function should be skipped
    (with optional reason).

    The test will only be skipped if the optional when argument is True (the 
    default value is True). 
    
    If when is False, the decorated test will be run. This is useful
    for conditional skipping of tests. E.g.:
    
    @skip("Skip this if using MicroPython", when=is_micropython)
    def test_something():
        assert 1 == 1
    """

    if when:
        def decorator(func):
            global _SKIPPED_TESTS
            _SKIPPED_TESTS.append(func)
            return func
    else:
        def decorator(func):
            return func

    return decorator


async def run(*args, **kwargs):
    """
    Run the test suite given args that specify the tests to run.

    The specification may be simply a string describing the directory in
    which to start looking for test modules (e.g. "./tests"), or strings
    representing the names of specific test modules / tests to run (of the
    form: "module_path" or "module_path::test_function"; e.g.
    "tests/test_module.py" or "tests/test_module.py::test_stuff").

    If a named `pattern` argument is provided, it will be used to match test
    modules in the specification for target directories. The default pattern is
    "test_*.py".

    If there is a conftest.py file in any of the specified directories
    containing a test module, it will be imported for any global setup and
    teardown functions to use for modules found within that directory. These
    setup and teardown functions can be overridden in the individual test
    modules.
    """
    targets = []
    pattern = kwargs.get("pattern", "test_*.py")
    for arg in args:
        if isinstance(arg, str):
            targets.append(arg)
        else:
            raise ValueError(f"Unexpected argument: {arg}")
    test_modules = discover(targets, pattern)
    module_count = len(test_modules)
    test_count = sum([len(module.tests) for module in test_modules])
    print(
        f"Found {module_count} test module[s]. Running {test_count} test[s].\n"
    )

    failed_tests = []
    skipped_tests = []
    passed_tests = []
    start = time.time()
    for module in test_modules:
        await module.run()
        for test in module.tests:
            if test.status == FAIL:
                failed_tests.append(test)
            elif test.status == SKIPPED:
                skipped_tests.append(test)
            elif test.status == PASS:
                passed_tests.append(test)
    end = time.time()
    print("")
    if failed_tests:
        print(
            "================================= \033[31;1mFAILURES\033[0m ================================="
        )
        for failed in failed_tests:
            print(
                "Failed: ",
                "\033[1m",
                failed.module_name,
                "::",
                failed.test_name,
                "\033[0m",
                sep="",
            )
            print(failed.traceback)
            if failed != failed_tests[-1]:
                print("")
    error_count = len(failed_tests)
    skip_count = len(skipped_tests)
    pass_count = test_count - error_count - skip_count
    dur = end - start
    print(
        "========================= short test summary info =========================="
    )
    print(
        f"\033[1m{error_count}\033[0m \033[31;1mfailed\033[0m, \033[1m{skip_count}\033[0m \033[33;1mskipped\033[0m, \033[1m{pass_count}\033[0m \033[32;1mpassed\033[0m in \033[1m{dur:.2f} seconds\033[0m"
    )
    return {
        "passes": [t.test_name for t in passed_tests],
        "fails": [t.test_name for t in failed_tests],
        "skipped": [t.test_name for t in skipped_tests],
    }
