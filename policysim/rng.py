"""Mulberry32 PRNG. Small, fast, and identical to the JavaScript version,
so Python and the web app reproduce the same run from the same seed."""

M32 = 0xFFFFFFFF


def _imul(x, y):
    return (x * y) & M32


class Mulberry32:
    def __init__(self, seed):
        self.a = int(seed) & M32

    def next(self):
        self.a = (self.a + 0x6D2B79F5) & M32
        a = self.a
        t = _imul(a ^ (a >> 15), a | 1)
        t = ((t + _imul(t ^ (t >> 7), t | 61)) & M32) ^ t
        return ((t ^ (t >> 14)) & M32) / 4294967296.0
