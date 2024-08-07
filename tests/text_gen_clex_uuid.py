import pytest
import requests
from unittest.mock import patch
from io import StringIO
import sys

# Import the main function from gen_clex_uuid
sys.path.insert(0, '../app')
from app.gen_clex_uuid import main

# Define test cases
test_cases = [
    (4, "x-stixd-clex", "https://raw.githubusercontent.com/ciioprof0/stixd/03c934281777fecd3edb1d8622310bbf0839c17d/tests/test_clex.pl", "x-stixd-clex--7440851b-4d8c-417b-8bc8-02df2dd1e96b"),
    (4, "x-stixd-clex", "https://raw.githubusercontent.com/Attempto/Clex/20960a5ce07776cb211a8cfb25dc8c81fcdf25e2/clex_lexicon.pl", "x-stixd-clex--b29ffdd4-c6bd-4c0b-a279-f184825f8114")
]

# Mock response content
mock_file_contents = {
    "https://raw.githubusercontent.com/ciioprof0/stixd/03c934281777fecd3edb1d8622310bbf0839c17d/tests/test_clex.pl": "mock content for ciioprof0 test_clex.pl",
    "https://raw.githubusercontent.com/Attempto/Clex/20960a5ce07776cb211a8cfb25dc8c81fcdf25e2/clex_lexicon.pl": "mock content for Attempto clex_lexicon.pl"
}

# Mock requests.get to return the mocked file content
class MockResponse:
    def __init__(self, url):
        self.url = url
        self.text = mock_file_contents[url]

    def raise_for_status(self):
        pass

@patch('requests.get', side_effect=lambda url: MockResponse(url))
@pytest.mark.parametrize("uuid_version, object_type, file_url, expected_stix_identifier", test_cases)
def test_generate_uuid(mock_get, uuid_version, object_type, file_url, expected_stix_identifier):
    # Capture the output
    captured_output = StringIO()
    sys.stdout = captured_output

    main(uuid_version, object_type, file_url)

    # Reset redirect.
    sys.stdout = sys.__stdout__

    # Check if expected output is in captured output
    assert expected_stix_identifier in captured_output.getvalue()
