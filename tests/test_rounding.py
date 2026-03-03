import pytest

from utils.rounding import round_price


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, 0),
        (1, 50),
        (49.99, 50),
        (50, 50),
        (74.99, 50),
        (75, 100),
        (99.99, 100),
        (100, 100),
        (149.9, 100),
        (150, 200),
        (999.9, 1000),
        (1000, 1000),
        (1250, 1200),  # nearest 100 without cartel
    ],
)
def test_round_price_normal(value, expected):
    assert round_price(value, is_cartel=False) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, 0),
        (1, 50),
        (49.99, 50),
        (50, 50),
        (74.99, 50),
        (75, 100),
        (99.99, 100),
        (100, 100),
        (999.9, 1000),  # <=1000 uses normal rule
        (1000, 1000),  # boundary: still normal rule
        (1000.01, 1000),  # >1000 -> nearest 500: 1000.01 -> 1000 (to 500 multiple)
        (1249.9, 1000),  # to 1000
        (1250, 1500),  # halfway up to 1500
        (1499.9, 1500),
        (1500, 1500),
        (9999.9, 10000),  # no special adjust (<10000)
        (10000, 9900),  # special adjust: >=10000 and multiple of 1000 -> -100
        (15000, 14900),  # special adjust
        (20000, 19900),  # special adjust
    ],
)
def test_round_price_cartel(value, expected):
    assert round_price(value, is_cartel=True) == expected


@pytest.mark.parametrize(
    "value",
    ["10,5", "100,00", "abc", None],
)
def test_round_price_input_normalization(value):
    # Should not raise and should return an int
    result = round_price(value, is_cartel=False)
    assert isinstance(result, int)
