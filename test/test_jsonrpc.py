#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from mock import MagicMock, patch
from uiautomator import JsonRPCMethod, JsonRPCClient
import os


class TestJsonRPCMethod_id(unittest.TestCase):

    def test_id(self):
        method = JsonRPCMethod("", "method", 30)
        self.assertTrue(isinstance(method.id(), str))
        self.assertTrue(len(method.id()) > 0)
        for i in range(100):
            self.assertNotEqual(method.id(), method.id())


class TestJsonRPCMethod_call(unittest.TestCase):
    def setUp(self):
        self.url = "http://localhost/jsonrpc"
        self.timeout = 20
        self.method_name = "ping"
        self.id = "fGasV62G"
        self.method = JsonRPCMethod(self.url, self.method_name, self.timeout)
        self.method.id = MagicMock()
        self.method.id.return_value = self.id
        self.urlopen_patch = patch('requests.post')
        self.urlopen = self.urlopen_patch.start()

    def tearDown(self):
        self.urlopen_patch.stop()

    def test_normal_call(self):
        return_mock = self.urlopen.return_value
        return_mock.status_code = 200 #.return_value = 200

        return_mock.json.return_value = {"result": "pong", "error": None, "id": "DKNCJDLDJJ"}
        self.assertEqual("pong", self.method())
        self.method.id.assert_called_once_with()

        return_mock.json.return_value = {"result": "pong", "id": "JDLSFJLILJEMNC"}
        self.assertEqual("pong", self.method())
        self.assertEqual("pong", self.method(1, 2, "str", {"a": 1}, ["1"]))
        self.assertEqual("pong", self.method(a=1, b=2))

    def test_normal_call_error(self):
        return_mock = self.urlopen.return_value

        return_mock.status_code = 500
        with self.assertRaises(Exception):
            self.method()

        return_mock.status_code = 200
        return_mock.json.return_value = {"result": "pong", "error": {"code": -513937, "message": "error message."}, "id": "fGasV62G"}
        with self.assertRaises(Exception):
            self.method()
        return_mock.json.assert_called_with()

        return_mock.status_code = 200
        return_mock.json.return_value = {"result": None, "error": None, "id": "fGasV62G"}
        with self.assertRaises(SyntaxError):
            self.method(1, 2, kwarg1="")


class TestJsonRPCClient(unittest.TestCase):

    def setUp(self):
        self.url = "http://localhost/jsonrpc"
        self.timeout = 20

    def test_jsonrpc(self):
        with patch('uiautomator.JsonRPCMethod') as JsonRPCMethod:
            client = JsonRPCClient(self.url, self.timeout, JsonRPCMethod)
            JsonRPCMethod.return_value = "Ok"
            self.assertEqual(client.ping, "Ok")
            JsonRPCMethod.assert_called_once_with(self.url, "ping", timeout=self.timeout)

            JsonRPCMethod.return_value = {"width": 10, "height": 20}
            self.assertEqual(client.info, {"width": 10, "height": 20})
            JsonRPCMethod.assert_called_with(self.url, "info", timeout=self.timeout)