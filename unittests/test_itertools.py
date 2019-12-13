import itertools

import pytest

import asyncstdlib as a

from .utility import sync, asyncify, awaitify


@sync
async def test_accumulate():
    async def reduction(x, y):
        return x + y

    for reducer in (reduction, lambda x, y: x + y):
        for itertype in (asyncify, list):
            assert await a.list(a.accumulate(itertype([0, 1]), reducer)) == list(
                itertools.accumulate([0, 1], lambda x, y: x + y)
            )
            assert await a.list(
                a.accumulate(itertype([0, 1, 2, 3, 4, 0, -5]), reducer)
            ) == list(itertools.accumulate([0, 1, 2, 3, 4, 0, -5], lambda x, y: x + y))
            assert await a.list(a.accumulate(itertype([12]), reducer)) == list(
                itertools.accumulate([12], lambda x, y: x + y)
            )
            assert await a.list(a.accumulate(itertype([1]), reducer, initial=23)) == [
                23,
                24,
            ]
            assert await a.list(a.accumulate(itertype([]), reducer, initial=42)) == [42]


@sync
async def test_accumulate_misuse():
    with pytest.raises(TypeError):
        assert await a.list(a.accumulate([]))


@sync
async def test_cycle():
    async for _ in a.cycle([]):
        assert False
    assert True
    async for idx, val in a.enumerate(a.cycle([0, 1])):
        assert idx % 2 == val
        if idx == 6:
            break
    assert idx == 6


chains = [
    ([0, 1, 2, 3], [4, 5, 6, 7]),
    ([4], [3], [2], [1]),
    ([], [], [], [1], [], []),
]


@pytest.mark.parametrize("iterables", chains)
@sync
async def test_chain(iterables):
    for itertype in (asyncify, list):
        assert await a.list(a.chain(*map(itertype, iterables))) == list(
            itertools.chain(*iterables)
        )
        assert await a.list(a.chain.from_iterable(map(itertype, iterables))) == list(
            itertools.chain.from_iterable(iterables)
        )


compress_cases = [
    (range(20), [idx % 2 for idx in range(20)]),
    ([1] * 5, [True, True, False, True, True]),
    ([1] * 128, [False]),
    ([], []),
]


@pytest.mark.parametrize("data, selectors", compress_cases)
@sync
async def test_compress(data, selectors):
    expected = list(itertools.compress(data, selectors))
    assert await a.list(a.compress(data, selectors)) == expected
    assert await a.list(a.compress(asyncify(data), selectors)) == expected
    assert await a.list(a.compress(data, asyncify(selectors))) == expected
    assert await a.list(a.compress(asyncify(data), asyncify(selectors))) == expected


dropwhile_cases = [
    (range(20), lambda x: x < 5),
    (range(20), lambda x: x > 5),
    ([1] * 12, lambda y: y > 5),
]


@pytest.mark.parametrize("iterable, predicate", dropwhile_cases)
@sync
async def test_dropwhile(iterable, predicate):
    expected = list(itertools.dropwhile(predicate, iterable))
    assert await a.list(a.dropwhile(predicate, iterable)) == expected
    assert await a.list(a.dropwhile(awaitify(predicate), iterable)) == expected
    assert await a.list(a.dropwhile(predicate, asyncify(iterable))) == expected
    assert (
        await a.list(a.dropwhile(awaitify(predicate), asyncify(iterable))) == expected
    )


@sync
async def test_islice():
    for iterable in ((), (1, 2, 3, 4), range(25), range(500)):
        for slicing in ((0,), (5,), (None, None, None), (0, 20, 3), (5, 0, 1)):
            print(slicing)
            expected = list(itertools.islice(iterable, *slicing))
            assert await a.list(a.islice(iterable, *slicing)) == expected
            assert await a.list(a.islice(asyncify(iterable), *slicing)) == expected