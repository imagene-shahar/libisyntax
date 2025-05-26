import os
import pytest
from python_isyntax import Isyntax

SAMPLE = os.path.join(os.path.dirname(__file__), "sample.isyntax")

@pytest.mark.skipif(not os.path.exists(SAMPLE), reason="sample file missing")
def test_open_slide():
    with Isyntax(SAMPLE) as img:
        assert img.level_count > 0
        assert len(img.level_dimensions) == img.level_count

@pytest.mark.skipif(not os.path.exists(SAMPLE), reason="sample file missing")
def test_read_region():
    with Isyntax(SAMPLE) as img:
        region = img.read_region((0, 0), 0, (128, 128))
        assert region.size == (128, 128)
