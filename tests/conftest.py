import pytest
from app import app as flask_app

@pytest.fixture
def app():
    """Create application for the tests."""
    print("Fixture 'app' is being called")
    flask_app.config.update({
        "TESTING": True,
    })
    yield flask_app

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner() 