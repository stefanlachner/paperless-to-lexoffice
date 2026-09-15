import contextlib
import io
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "source"))
import paperless


class DocumentSearchTests(unittest.TestCase):
    def response(self, ids, next_page=None, **extra):
        response = Mock()
        response.url = "https://paperless.example/api/documents/?page=1"
        response.json.return_value = {
            "results": [{"id": value} for value in ids],
            "next": next_page,
            **extra,
        }
        return response

    def setUp(self):
        self.output = contextlib.redirect_stdout(io.StringIO())
        self.output.__enter__()
        self.addCleanup(self.output.__exit__, None, None, None)

    @patch("paperless.requests.get")
    def test_search_reads_all_pages_and_ignores_legacy_all(self, get):
        get.side_effect = [self.response([4], "?page=2", all=[99]), self.response([5])]
        self.assertEqual(paperless.search_documents("test-token", "https://paperless.example/", "invoice & tax"), [4, 5])
        self.assertEqual(get.call_args_list[0].kwargs["params"], {"query": "(invoice & tax)"})
        self.assertEqual(get.call_args_list[1].args[0], "https://paperless.example/api/documents/?page=2")
        self.assertIsNone(get.call_args_list[1].kwargs["params"])

    @patch("paperless.requests.get")
    def test_tag_filter_reads_pages_and_removes_duplicate_ids(self, get):
        get.side_effect = [self.response([7, 8], "/api/documents/?page=2"), self.response([8, 9])]
        self.assertEqual(paperless.filter_documents_by_tags("test-token", "https://paperless.example", [1, "2"]), [7, 8, 9])
        self.assertEqual(get.call_args_list[0].kwargs["params"], {"tags__id__all": "1,2"})

    @patch("paperless.requests.get")
    def test_empty_results(self, get):
        get.return_value = self.response([])
        self.assertEqual(paperless.search_documents("test-token", "https://paperless.example", "missing"), [])

    @patch("paperless.requests.get")
    def test_later_page_error_returns_no_partial_ids(self, get):
        failed = self.response([])
        failed.raise_for_status.side_effect = paperless.requests.HTTPError("503")
        get.side_effect = [self.response([1], "?page=2"), failed]
        self.assertIsNone(paperless.filter_documents_by_tags("test-token", "https://paperless.example", [1]))

    @patch("paperless.requests.get")
    def test_invalid_response_returns_no_ids(self, get):
        for payload in ({"all": [1], "next": None}, {"results": None, "next": None}, {"results": [{"id": "1"}], "next": None}):
            with self.subTest(payload=payload):
                get.return_value.json.return_value = payload
                self.assertIsNone(paperless.search_documents("test-token", "https://paperless.example", "invoice"))

    @patch("paperless.requests.get")
    def test_cross_origin_next_is_not_requested(self, get):
        get.return_value = self.response([1], "https://other.example/api/documents/")
        self.assertIsNone(paperless.search_documents("test-token", "https://paperless.example", "invoice"))
        self.assertEqual(get.call_count, 1)

    @patch("paperless.requests.get")
    def test_repeated_page_stops(self, get):
        get.return_value = self.response([1], "https://paperless.example/api/documents/")
        self.assertIsNone(paperless.search_documents("test-token", "https://paperless.example", "invoice"))
        self.assertEqual(get.call_count, 1)


if __name__ == "__main__":
    unittest.main()
