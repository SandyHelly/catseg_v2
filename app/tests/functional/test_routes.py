import sys
sys.path.append(".")

from app import app

def test_get_pages():
    """
    check that the response is valid
    """

    with app.test_client() as test_client:
        response = test_client.get('/')
        assert response.status_code == 200