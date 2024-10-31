import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    """Test the main index route returns 200"""
    rv = client.get('/')
    assert rv.status_code == 200

def test_health_check(client):
    """Test the health check endpoint"""
    rv = client.get('/health')
    assert rv.status_code == 200
    assert rv.json['status'] == 'healthy'

def test_basic_pattern_route(client):
    """Test the basic pattern route returns 200"""
    rv = client.get('/basic/')
    assert rv.status_code == 200
