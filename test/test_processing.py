from app.utils import clean_name


def test_clean_name():

    text = "UPI/DR/12345/AMAZON/XYZ"

    result = clean_name(text)

    assert isinstance(result, str)
