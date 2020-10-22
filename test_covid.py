import pytest
from datetime import date
from covid import date_range


def test_date_range():
    assert isinstance(date_range(date(2020, 5, 1), date(2020, 5, 31)), list)
    assert len(date_range(date(2020, 5, 1), date(2020, 5, 31))) == 31


def test_date_range_input():
    with pytest.raises(TypeError):
        date_range('2020-10-01', '2020-10-05')
        date_range(15, 31)
        date_range([date(2020, 1, 22), date.today()])


def test_date_range_out_of_range():
    with pytest.raises(ValueError):
        date_range(date(2020, 1, 1), date(2020, 6, 15))
        date_range(date(2020, 10, 5), date(2020, 3, 14))
