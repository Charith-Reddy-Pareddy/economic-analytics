import requests
from src.fetchers import chunks, fetch_world_bank

class Response:
    def __init__(self, payload): self.payload = payload
    def raise_for_status(self): return None
    def json(self): return self.payload

class Session:
    def get(self, url, params, timeout):
        if url.endswith("/country"):
            return Response([{}, [{"id":"IND","name":"India","region":{"id":"SAS"}}, {"id":"USA","name":"United States","region":{"id":"NAC"}}, {"id":"WLD","name":"World","region":{"id":"NA"}}]])
        if "IND;USA" in url:
            return Response([{}, [{"countryiso3code":"IND","date":"2023","value":6.0}, {"countryiso3code":"USA","date":"2023","value":2.5}]])
        raise requests.RequestException("temporary upstream failure")

def test_chunks_preserve_all_values():
    assert list(chunks(["A", "B", "C"], 2)) == [["A", "B"], ["C"]]

def test_world_bank_keeps_successful_batches_when_one_fails():
    result = fetch_world_bank(start_year=2023, batch_size=2, session=Session())
    assert len(result) == 4
    assert set(result[0][1]["country_code"]) == {"IND", "USA"}
