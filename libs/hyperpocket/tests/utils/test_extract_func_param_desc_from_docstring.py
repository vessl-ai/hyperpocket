import unittest

from hyperpocket.util.extract_func_param_desc_from_docstring import extract_param_docstring_mapping


class TestExtractFuncParamDescFromDocstring(unittest.TestCase):
    def test_extract_google_style_param_case1(self):
        def style_func(a: int, b: int):
            """
            Style Function

            Args:
                a(int): first
                b(int): second
            """
            pass

        params = extract_param_docstring_mapping(style_func)
        self.assertEqual(params, {'a': 'first', 'b': 'second'})

    def test_extract_google_style_param_case2(self):
        def style_func(a: int, b: int):
            """
            Style Function

            Args:
                - a (int) : first
                - b (int) : second
            """
            pass

        params = extract_param_docstring_mapping(style_func)
        self.assertEqual(params, {'a': 'first', 'b': 'second'})

    def test_extract_google_style_param_case3(self):
        def style_func(a: int, b: int):
            """
            Style Function

            Args:
                1. a (int) : first
                2. b (int) : second
            """
            pass

        params = extract_param_docstring_mapping(style_func)
        self.assertEqual(params, {'a': 'first', 'b': 'second'})

    def test_extract_other_style_param_case1(self):
        def style_func(a: int, b: int):
            """
            Style Function

            :param: a: first
            :param: b: second
            """
            pass

        params = extract_param_docstring_mapping(style_func)
        self.assertEqual(params, {'a': 'first', 'b': 'second'})

    def test_extract_other_style_param_case2(self):
        def style_func(a: int, b: int):
            """
            Style Function

            :param: a(int): first
            :param: b(int): second
            """
            pass

        params = extract_param_docstring_mapping(style_func)
        self.assertEqual(params, {'a': 'first', 'b': 'second'})

    def test_extract_other_style_param_case3(self):
        def style_func(a: int, b: int):
            """
            Style Function

            @param: a: first
            @param: b: second
            """
            pass

        params = extract_param_docstring_mapping(style_func)
        self.assertEqual(params, {'a': 'first', 'b': 'second'})

    def test_extract_other_style_param_case4(self):
        def style_func(a: int, b: int):
            """
            Style Function

            @param a(int): first
            @param b(int): second
            """
            pass

        params = extract_param_docstring_mapping(style_func)
        self.assertEqual(params, {'a': 'first', 'b': 'second'})

    def test_extract_other_style_param_case5(self):
        def style_func(a: int, b: int):
            """
            Style Function

            @arg: a: first
            @arg: b: second
            """
            pass

        params = extract_param_docstring_mapping(style_func)
        self.assertEqual(params, {'a': 'first', 'b': 'second'})

    def test_extract_other_style_param_case6(self):
        def style_func(a: int, b: int):
            """
            Style Function

            @arg a(int): first
            @arg b(int): second
            """
            pass

        params = extract_param_docstring_mapping(style_func)
        self.assertEqual(params, {'a': 'first', 'b': 'second'})

    def test_extract_other_style_param_case7(self):
        def style_func(a: int, b: int):
            """
            Style Function

            :arg: a: first
            :arg: b: second
            """
            pass

        params = extract_param_docstring_mapping(style_func)
        self.assertEqual(params, {'a': 'first', 'b': 'second'})

    def test_extract_other_style_param_case8(self):
        def style_func(a: int, b: int):
            """
            Style Function

            :arg a(int): first
            :arg b(int): second
            """
            pass

        params = extract_param_docstring_mapping(style_func)
        self.assertEqual(params, {'a': 'first', 'b': 'second'})

    def test_extract_plain_style_param_case1(self):
        def style_func(a: int, b: int):
            """
            Style Function

            a(int) : first
            b(int) : second
            """
            pass

        params = extract_param_docstring_mapping(style_func)
        self.assertEqual(params, {'a': 'first', 'b': 'second'})

    def test_extract_plain_style_param_case2(self):
        def style_func(a: int, b: int):
            """
            Style Function

            - a(int) : first
            - b(int) : second
            """
            pass

        params = extract_param_docstring_mapping(style_func)
        self.assertEqual(params, {'a': 'first', 'b': 'second'})

    def test_extract_plain_style_param_case3(self):
        def style_func(a: int, b: int):
            """
            a: first
            b: second
            """
            pass

        params = extract_param_docstring_mapping(style_func)
        self.assertEqual(params, {'a': 'first', 'b': 'second'})
