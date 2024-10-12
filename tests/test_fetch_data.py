import pytest
from unittest.mock import patch
from fetch_data import fetch_data


ENDPOINT = 'https://apiv3.iucnredlist.org/api/v3/'


class TestFetchData:

    # Test fetching version
    def test_fetch_data_version(self):
        endpoint = ENDPOINT + 'version'
        result = fetch_data(endpoint)

        assert isinstance(result, dict)
        assert result.get('version') is not None

    # Test fetching country list (No token)
    def test_fetch_country_list_failure_no_token(self):
        endpoint = ENDPOINT + 'country/list'
        result = fetch_data(endpoint)

        assert isinstance(result, dict)
        assert result.get('error') is not None

    # Test fetching country list with incorrect token (Expect 500)
    @patch('fetch_data.requests.get')
    def test_fetch_country_list_failure_incorrect_token(self, mock_get):
        # Mocking a 500 response
        mock_get.return_value.status_code = 500
        mock_get.return_value.json.return_value = {
            "error": "Internal Server Error"}

        endpoint = ENDPOINT + 'country/list?token=69'
        result = fetch_data(endpoint)

        # Ensure fetch_data handles 500 properly
        assert result is None or result.get('error') == "Internal Server Error"
