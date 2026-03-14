"""
Unit tests for the Axiom Python SDK

Run with: python -m pytest test_axiom_sdk.py
"""

import json
import unittest
from unittest.mock import Mock, patch, MagicMock
from axiom_sdk import inject_tools, ToolExecutionError, _make_tool_caller


class TestToolInjection(unittest.TestCase):
    def test_inject_tools_basic(self):
        """Test basic tool injection into globals"""
        globals_dict = {}
        tools_config = {
            "api_base": "http://localhost:8080/api",
            "token": "test-token",
            "tools": [
                {"name": "vector_search", "description": "Search vectors"},
                {"name": "slack_send", "description": "Send message"}
            ]
        }
        
        inject_tools(globals_dict, tools_config)
        
        # Check that tools were injected
        self.assertIn("vector_search", globals_dict)
        self.assertIn("slack_send", globals_dict)
        self.assertTrue(callable(globals_dict["vector_search"]))
        self.assertTrue(callable(globals_dict["slack_send"]))
    
    def test_inject_tools_missing_config(self):
        """Test that missing api_base or token raises error"""
        globals_dict = {}
        
        # Missing api_base
        with self.assertRaises(ValueError):
            inject_tools(globals_dict, {"token": "test"})
        
        # Missing token
        with self.assertRaises(ValueError):
            inject_tools(globals_dict, {"api_base": "http://localhost"})
    
    def test_inject_tools_empty_tools_list(self):
        """Test injection with empty tools list"""
        globals_dict = {}
        tools_config = {
            "api_base": "http://localhost:8080/api",
            "token": "test-token",
            "tools": []
        }
        
        inject_tools(globals_dict, tools_config)
        
        # Should not inject any tools
        self.assertEqual(len(globals_dict), 0)
    
    def test_tool_function_metadata(self):
        """Test that injected functions have correct metadata"""
        globals_dict = {}
        tools_config = {
            "api_base": "http://localhost:8080/api",
            "token": "test-token",
            "tools": [
                {"name": "my_tool", "description": "My custom tool"}
            ]
        }
        
        inject_tools(globals_dict, tools_config)
        
        tool_func = globals_dict["my_tool"]
        self.assertEqual(tool_func.__name__, "my_tool")
        self.assertEqual(tool_func.__doc__, "My custom tool")


class TestToolCaller(unittest.TestCase):
    @patch('axiom_sdk.urllib.request.urlopen')
    def test_successful_tool_call(self, mock_urlopen):
        """Test successful tool execution"""
        # Mock successful HTTP response
        mock_response = Mock()
        mock_response.read.return_value = json.dumps({
            "success": True,
            "result": {"data": [1, 2, 3]}
        }).encode('utf-8')
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response
        
        # Create tool caller
        tool_func = _make_tool_caller(
            "http://localhost:8080/api",
            "test-token",
            "vector_search"
        )
        
        # Call tool
        result = tool_func(query="test", limit=5)
        
        # Verify result
        self.assertEqual(result, {"data": [1, 2, 3]})
        
        # Verify HTTP request
        self.assertTrue(mock_urlopen.called)
        call_args = mock_urlopen.call_args
        request = call_args[0][0]
        self.assertEqual(request.get_full_url(), "http://localhost:8080/api")
        self.assertEqual(request.get_header('Authorization'), 'Bearer test-token')
    
    @patch('axiom_sdk.urllib.request.urlopen')
    def test_tool_call_with_error(self, mock_urlopen):
        """Test tool call that returns an error"""
        mock_response = Mock()
        mock_response.read.return_value = json.dumps({
            "success": False,
            "error": "Tool execution failed"
        }).encode('utf-8')
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response
        
        tool_func = _make_tool_caller(
            "http://localhost:8080/api",
            "test-token",
            "vector_search"
        )
        
        # Should raise ToolExecutionError
        with self.assertRaises(ToolExecutionError) as context:
            tool_func(query="test")
        
        self.assertIn("Tool execution failed", str(context.exception))
    
    @patch('axiom_sdk.urllib.request.urlopen')
    def test_tool_call_http_error(self, mock_urlopen):
        """Test tool call with HTTP error"""
        from urllib.error import HTTPError
        
        mock_error = HTTPError(
            "http://localhost:8080/api",
            401,
            "Unauthorized",
            {},
            None
        )
        mock_urlopen.side_effect = mock_error
        
        tool_func = _make_tool_caller(
            "http://localhost:8080/api",
            "test-token",
            "vector_search"
        )
        
        with self.assertRaises(ToolExecutionError) as context:
            tool_func(query="test")
        
        self.assertIn("HTTP error 401", str(context.exception))
    
    @patch('axiom_sdk.urllib.request.urlopen')
    def test_tool_call_network_error(self, mock_urlopen):
        """Test tool call with network error"""
        from urllib.error import URLError
        
        mock_urlopen.side_effect = URLError("Connection refused")
        
        tool_func = _make_tool_caller(
            "http://localhost:8080/api",
            "test-token",
            "vector_search"
        )
        
        with self.assertRaises(ToolExecutionError) as context:
            tool_func(query="test")
        
        self.assertIn("network error", str(context.exception))
    
    @patch('axiom_sdk.urllib.request.urlopen')
    def test_tool_call_invalid_json(self, mock_urlopen):
        """Test tool call with invalid JSON response"""
        mock_response = Mock()
        mock_response.read.return_value = b"not valid json"
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response
        
        tool_func = _make_tool_caller(
            "http://localhost:8080/api",
            "test-token",
            "vector_search"
        )
        
        with self.assertRaises(ToolExecutionError) as context:
            tool_func(query="test")
        
        self.assertIn("invalid JSON response", str(context.exception))
    
    @patch('axiom_sdk.urllib.request.urlopen')
    def test_tool_call_request_payload(self, mock_urlopen):
        """Test that tool call sends correct payload"""
        mock_response = Mock()
        mock_response.read.return_value = json.dumps({
            "success": True,
            "result": {}
        }).encode('utf-8')
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response
        
        tool_func = _make_tool_caller(
            "http://localhost:8080/api",
            "test-token",
            "my_tool"
        )
        
        # Call with specific arguments
        tool_func(arg1="value1", arg2=42, arg3=True)
        
        # Get the request object
        request = mock_urlopen.call_args[0][0]
        
        # Verify request data
        payload = json.loads(request.data.decode('utf-8'))
        self.assertEqual(payload["tool_name"], "my_tool")
        self.assertEqual(payload["arguments"]["arg1"], "value1")
        self.assertEqual(payload["arguments"]["arg2"], 42)
        self.assertEqual(payload["arguments"]["arg3"], True)


class TestIntegration(unittest.TestCase):
    @patch('axiom_sdk.urllib.request.urlopen')
    def test_end_to_end_workflow(self, mock_urlopen):
        """Test complete workflow of injecting and calling tools"""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.read.return_value = json.dumps({
            "success": True,
            "result": {"matches": ["doc1", "doc2", "doc3"]}
        }).encode('utf-8')
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response
        
        # Simulate code execution environment
        exec_globals = {}
        
        tools_config = {
            "api_base": "http://cortex/api/tools/invoke",
            "token": "exec-token-123",
            "tools": [
                {"name": "vector_search", "description": "Search vectors"}
            ]
        }
        
        # Inject tools
        inject_tools(exec_globals, tools_config)
        
        # User code would do this:
        result = exec_globals["vector_search"](query="test query", limit=10)
        
        # Verify result
        self.assertEqual(result["matches"], ["doc1", "doc2", "doc3"])
        
        # Verify HTTP call was made correctly
        request = mock_urlopen.call_args[0][0]
        self.assertIn("exec-token-123", request.get_header('Authorization'))
        
        payload = json.loads(request.data.decode('utf-8'))
        self.assertEqual(payload["tool_name"], "vector_search")
        self.assertEqual(payload["arguments"]["query"], "test query")
        self.assertEqual(payload["arguments"]["limit"], 10)


if __name__ == '__main__':
    unittest.main()
