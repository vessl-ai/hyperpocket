import unittest

from hyperpocket.util.extract_func_param_desc_from_docstring import (
    extract_param_docstring_mapping,
)


class TestExtractFuncParamDescFromDocstring(unittest.TestCase):
    def test_extract_google_style_param_case1(self):
        def style_func(a: int, b: int):
            """
            Style Function

            Args:
                a(int): first desc
                b(int): second desc
            """
            pass

        params = extract_param_docstring_mapping(style_func)
        self.assertEqual(params, {"a": "first desc", "b": "second desc"})

    def test_extract_google_style_param_case2(self):
        def style_func(a: int, b: int):
            """
            Style Function

            Args:
                - a (int) : first desc
                - b (int) : second desc
            """
            pass

        params = extract_param_docstring_mapping(style_func)
        self.assertEqual(params, {"a": "first desc", "b": "second desc"})

    def test_extract_google_style_param_case3(self):
        def style_func(a: int, b: int):
            """
            Style Function

            Args:
                1. a (int) : first desc
                2. b (int) : second desc
            """
            pass

        params = extract_param_docstring_mapping(style_func)
        self.assertEqual(params, {"a": "first desc", "b": "second desc"})

    def test_extract_other_style_param_case1(self):
        def style_func(a: int, b: int):
            """
            Style Function

            :param: a: first desc
            :param: b: second desc
            """
            pass

        params = extract_param_docstring_mapping(style_func)
        self.assertEqual(params, {"a": "first desc", "b": "second desc"})

    def test_extract_other_style_param_case2(self):
        def style_func(a: int, b: int):
            """
            Style Function

            :param: a(int): first desc
            :param: b(int): second desc
            """
            pass

        params = extract_param_docstring_mapping(style_func)
        self.assertEqual(params, {"a": "first desc", "b": "second desc"})

    def test_extract_other_style_param_case3(self):
        def style_func(a: int, b: int):
            """
            Style Function

            @param: a: first desc
            @param: b: second desc
            """
            pass

        params = extract_param_docstring_mapping(style_func)
        self.assertEqual(params, {"a": "first desc", "b": "second desc"})

    def test_extract_other_style_param_case4(self):
        def style_func(a: int, b: int):
            """
            Style Function

            @param a(int): first desc
            @param b(int): second desc
            """
            pass

        params = extract_param_docstring_mapping(style_func)
        self.assertEqual(params, {"a": "first desc", "b": "second desc"})

    def test_extract_other_style_param_case5(self):
        def style_func(a: int, b: int):
            """
            Style Function

            @arg: a: first desc
            @arg: b: second desc
            """
            pass

        params = extract_param_docstring_mapping(style_func)
        self.assertEqual(params, {"a": "first desc", "b": "second desc"})

    def test_extract_other_style_param_case6(self):
        def style_func(a: int, b: int):
            """
            Style Function

            @arg a(int): first desc
            @arg b(int): second desc
            """
            pass

        params = extract_param_docstring_mapping(style_func)
        self.assertEqual(params, {"a": "first desc", "b": "second desc"})

    def test_extract_other_style_param_case7(self):
        def style_func(a: int, b: int):
            """
            Style Function

            :arg: a: first desc
            :arg: b: second desc
            """
            pass

        params = extract_param_docstring_mapping(style_func)
        self.assertEqual(params, {"a": "first desc", "b": "second desc"})

    def test_extract_other_style_param_case8(self):
        def style_func(a: int, b: int):
            """
            Style Function

            :arg a(int): first desc
            :arg b(int): second desc
            """
            pass

        params = extract_param_docstring_mapping(style_func)
        self.assertEqual(params, {"a": "first desc", "b": "second desc"})

    def test_extract_other_style_param_case9(self):
        def style_func(a: int, b: int):
            """
            Style Function

            @arg a first desc
            @arg b second desc
            """
            pass

        params = extract_param_docstring_mapping(style_func)
        self.assertEqual(params, {"a": "first desc", "b": "second desc"})

    def test_extract_other_style_param_case10(self):
        def style_func(a: int, b: int):
            """
            Style Function

            :arg a first desc
            :arg b second desc
            """
            pass

        params = extract_param_docstring_mapping(style_func)
        self.assertEqual(params, {"a": "first desc", "b": "second desc"})

    def test_extract_plain_style_param_case1(self):
        def style_func(a: int, b: int):
            """
            Style Function

            a(int) : first desc
            b(int) : second desc
            """
            pass

        params = extract_param_docstring_mapping(style_func)
        self.assertEqual(params, {"a": "first desc", "b": "second desc"})

    def test_extract_plain_style_param_case2(self):
        def style_func(a: int, b: int):
            """
            Style Function

            - a(int) : first desc
            - b(int) : second desc
            """
            pass

        params = extract_param_docstring_mapping(style_func)
        self.assertEqual(params, {"a": "first desc", "b": "second desc"})

    def test_extract_plain_style_param_case3(self):
        def style_func(a: int, b: int):
            """
            a: first desc
            b: second desc
            """
            pass

        params = extract_param_docstring_mapping(style_func)
        self.assertEqual(params, {"a": "first desc", "b": "second desc"})
