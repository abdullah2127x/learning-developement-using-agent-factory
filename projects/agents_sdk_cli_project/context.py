from contextlib import ExitStack, contextmanager

@contextmanager
def A():
    print("enter A")
    try:
        yield "apple"
    finally:
        print("exit A")


@contextmanager
def B():
    print("enter B")
    # raise RuntimeError("B exploded before entering")
    yield "banana"
    print("exit B")

@contextmanager
def C():
    print("enter C")
    try:
        yield "cherry"
    finally:
        print("exit C")


with ExitStack() as stack:
    a = stack.enter_context(A())
    b = stack.enter_context(B())   # ← crash happens here
    c = stack.enter_context(C())

    print("inside block", a, b, c)