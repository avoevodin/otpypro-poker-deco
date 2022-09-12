from functools import update_wrapper


class CallsCount(object):
    def __init__(self):
        self.calls = 0

    def __str__(self):
        return f"{self.calls}"

    def add_call(self):
        self.calls += 1


def disable():
    """
    Disable a decorator by re-assigning the decorator's name
    to this function. For example, to turn off memoization:

    >>> memo = disable

    """
    return


def decorator(wrapped):
    """
    Decorate a decorator so that it inherits the docstrings
    and stuff from the function it's decorating.
    """

    def decorator_update_wrapper(decorator_to_update):
        return update_wrapper(decorator_to_update, wrapped)

    return decorator_update_wrapper


def countcalls(func):
    """Decorator that counts calls made to the function decorated."""

    # @wraps(func)
    @decorator(func)
    def wrapper(*args, **kwargs):
        wrapper.calls.add_call()
        # print(f"Function {func.__name__!r} was called {wrapper.calls}x")
        return func(*args, **kwargs)

    wrapper.calls = CallsCount()
    return wrapper


def memo(func):
    """
    Memoize a function so that it caches all return values for
    faster future lookups.
    """

    kwd_mark = object()

    # @wraps(func)
    @decorator(func)
    def wrapper(*args, **kwargs):
        key = hash(args + (kwd_mark,) + tuple(sorted(kwargs.items())))
        result = wrapper.cache.get(key)
        if not result:
            result = func(*args, **kwargs)
            wrapper.cache[key] = result
        elif hasattr(wrapper, "calls"):
            wrapper.calls.add_call()
        return result

    wrapper.cache = {}
    return wrapper


def n_ary(func):
    """
    Given binary function f(x, y), return an n_ary function such
    that f(x, y, z) = f(x, f(y,z)), etc. Also allow f(x) = x.
    """

    # @wraps(func)
    @decorator(func)
    def wrapper(*args):
        if len(args) == 1:
            return args[0]
        elif len(args) > 2:
            return wrapper(*args[:-2], func(*args[-2:]))
        else:
            return func(*args)

    return wrapper


def trace_args_decorator(decorator_to_enhance):
    def decorator_maker(prefix="____"):
        def decorator_wrapper(func):

            return decorator_to_enhance(func, prefix)

        return decorator_wrapper

    return decorator_maker


@trace_args_decorator
def trace(func, prefix):
    """Trace calls made to function decorated.

    @trace("____")
    def fib(n):
        ....

    >>> fib(3)
     --> fib(3)
    ____ --> fib(2)
    ________ --> fib(1)
    ________ <-- fib(1) == 1
    ________ --> fib(0)
    ________ <-- fib(0) == 1
    ____ <-- fib(2) == 2
    ____ --> fib(1)
    ____ <-- fib(1) == 1
     <-- fib(3) == 3

    """

    # @wraps(func)
    @decorator(func)
    def wrapper(*args, **kwargs):
        current_prefix = wrapper.prefix
        wrapper.prefix += prefix

        args_str = ", ".join([str(i) for i in args])
        kwargs_str = ", ".join([f"{k}={v}" for k, v in kwargs])
        all_args_str = ", ".join(filter(lambda x: x, (args_str, kwargs_str)))

        print(current_prefix, "-->", f"{func.__name__}({all_args_str})")
        result = func(*args, **kwargs)
        print(
            current_prefix,
            "<--",
            f"{func.__name__}({all_args_str}) == {result}",
        )

        wrapper.prefix = wrapper.prefix[: -len(prefix)]
        return result

    wrapper.prefix = ""
    return wrapper


@memo
@countcalls
@n_ary
def foo(a, b):
    return a + b


@countcalls
@memo
@n_ary
def bar(a, b):
    return a * b


@countcalls
@trace("####")
@memo
def fib(n):
    """Some doc"""
    return 1 if n <= 1 else fib(n - 1) + fib(n - 2)


def main():
    print(foo(4, 3))
    print(foo(4, 3, 2))
    print(foo(4, 3))
    print("foo was called", foo.calls, "times")

    print(bar(4, 3))
    print(bar(4, 3, 2))
    print(bar(4, 3, 2, 1))
    print("bar was called", bar.calls, "times")

    print(fib.__doc__)
    fib(3)
    print(fib.calls, "calls made")


if __name__ == "__main__":
    main()
