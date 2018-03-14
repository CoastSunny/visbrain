"""Test functions in others.py."""
from visbrain.utils.others import (get_dsf, set_if_not_none, find_closest_divisor)
from visbrain.io.path import get_data_path


class TestOthers(object):
    """Test functions in others.py."""

    def test_get_dsf(self):
        """Test function get_dsf."""
        assert get_dsf(100, 1000.) == (10, 100.)
        assert get_dsf(100, None) == (1, None)

    def test_find_closest_divisor(self):
        """Test function find_closest_divisor."""
        assert find_closest_divisor(1024, 200) == 256.
        assert find_closest_divisor(256, 100) == 128.

    def test_set_if_not_none(self):
        """Test function set_if_not_none."""
        a = 5.
        assert set_if_not_none(a, None) == 5.
        assert set_if_not_none(a, 10., False) == 5.
        assert set_if_not_none(a, 10.) == 10.

    def test_get_data_path(self):
        """Test function get_data_path."""
        assert isinstance(get_data_path(), str)
