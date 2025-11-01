import unittest
from mcp_server import handle_message, make_response

class TestFASTMCP(unittest.TestCase):
    def test_subtract(self):
        req = {"id": 5, "type": "request", "method": "subtract", "params": {"a": 10, "b": 3}}
        res = handle_message(req)
        self.assertEqual(res, {"difference": 7})
    def test_echo(self):
        req = {"id": 1, "type": "request", "method": "echo", "params": {"message": "hi"}}
        res = handle_message(req)
        self.assertEqual(res, {"echo": "hi"})

    def test_add(self):
        req = {"id": 2, "type": "request", "method": "add", "params": {"a": 2, "b": 3}}
        res = handle_message(req)
        self.assertEqual(res, {"sum": 5})

    def test_time(self):
        req = {"id": 3, "type": "request", "method": "time"}
        res = handle_message(req)
        self.assertIn("time", res)

    def test_error(self):
        req = {"id": 4, "type": "request", "method": "unknown"}
        with self.assertRaises(ValueError):
            handle_message(req)

if __name__ == "__main__":
    unittest.main()
