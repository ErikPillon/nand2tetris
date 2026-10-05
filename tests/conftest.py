import random

import pytest


@pytest.fixture
def rng() -> random.Random:
    """Deterministic randomness: the same failures every run, so you can debug."""
    return random.Random(20261003)
