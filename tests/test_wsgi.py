from app import app, server


def test_wsgi_server_is_exposed_for_gunicorn():
    assert server is app.server
