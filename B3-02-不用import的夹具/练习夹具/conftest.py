from __future__ import annotations

import pytest

@pytest.fixture
def phone() -> str:
    return "400-100-1000"