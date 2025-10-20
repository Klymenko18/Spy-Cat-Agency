import pytest

@pytest.fixture(autouse=True)
def catapi_ok(monkeypatch):
    class Resp:
        status_code = 200
        def json(self):
            return [{"id":"siam","name":"Siamese"},{"id":"norw","name":"Norwegian Forest Cat"}]
    monkeypatch.setattr("apps.core.services.requests.get", lambda *a, **k: Resp())
