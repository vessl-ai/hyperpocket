from unittest import TestCase

from pydantic import BaseModel

from hyperpocket.auth import AuthProvider
from hyperpocket.tool.function.annotation import function_tool
from hyperpocket.tool.function.tool import FunctionTool
from hyperpocket.util.flatten_json_schema import flatten_json_schema


class TestFunctionTool(TestCase):
    def test_function_tool_call(self):
        # given
        @function_tool
        def add_numbers(a: int, b: int):
            """
            add two numbers
            a(int): first name
            b(int): second name
            """
            return a + b

        # when
        result = add_numbers.invoke(body={"a": 1, "b": 2})

        # then
        self.assertEqual(result, "3")

    def test_function_tool_variables(self):
        @function_tool(
            tool_vars={
                "a": "1",
                "b": "2",
            },
        )
        def always_three(**kwargs):
            a = int(kwargs["a"])
            b = int(kwargs["b"])
            return str(a + b)

        result = always_three.invoke(body={})
        self.assertEqual(result, "3")

    def test_function_tool_overridden_variables(self):
        @function_tool(
            tool_vars={
                "a": "1",
                "b": "1",
            },
        )
        def always_two(**kwargs):
            a = int(kwargs["a"])
            b = int(kwargs["b"])
            return str(a + b)

        always_two.override_tool_variables(
            {
                "a": "1",
                "b": "2",
            }
        )
        result = always_two.invoke(body={})
        self.assertEqual(result, "3")

    def test_function_tool_overridden_variables_from_func(self):
        @function_tool(
            tool_vars={
                "a": "1",
                "b": "1",
            },
        )
        def always_two(**kwargs):
            a = int(kwargs["a"])
            b = int(kwargs["b"])
            return str(a + b)

        tool = FunctionTool.from_func(
            always_two,
            tool_vars={
                "a": "1",
                "b": "2",
            },
        )
        result = tool.invoke(body={})
        self.assertEqual(result, "3")

    def test_pydantic_input_function_tool_call(self):
        # given
        class FirstNumber(BaseModel):
            first: int

        class SecondNumber(BaseModel):
            second: int

        @function_tool
        def add_numbers(a: FirstNumber, b: SecondNumber):
            """
            add two numbers
            a(FirstNumber): first number
            b(SecondNumber): second number
            """
            return a.first + b.second

        # when
        result = add_numbers.invoke(
            body={
                "a": {
                    "first": 1,
                },
                "b": {"second": 2},
            }
        )

        # then
        self.assertEqual(result, "3")

    def test_register_no_auth_no_init_func_case(self):
        """
        Test register functionTool in case of no-auth and no-init function
        """

        @function_tool
        def add_numbers(a: int, b: int):
            """
            add two numbers
            a(int): first name
            b(int): second name
            """
            return a + b

        # when
        result = add_numbers.invoke(body={"a": 1, "b": 2})

        # then
        self.assertIsInstance(add_numbers, FunctionTool)
        self.assertEqual(result, "3")

    def test_register_no_auth_init_func_case(self):
        """
        Test register functionTool in case of no-auth and init function
        """

        @function_tool()
        def add_numbers(a: int, b: int):
            """
            add two numbers
            a(int): first name
            b(int): second name
            """
            return a + b

        # when
        result = add_numbers.invoke(body={"a": 1, "b": 2})

        # then
        self.assertIsInstance(add_numbers, FunctionTool)
        self.assertEqual(result, "3")

    def test_register_auth_init_func_case(self):
        """
        Test register functionTool in case of auth and init function

        """

        @function_tool(auth_provider=AuthProvider.SLACK)
        def add_numbers(a: int, b: int):
            """
            add two numbers
            a(int): first name
            b(int): second name
            """
            return a + b

        # when
        result = add_numbers.invoke(
            body={"a": 1, "b": 2}, envs={"SLACK_BOT_TOKEN": "test"}
        )

        # then
        self.assertIsInstance(add_numbers, FunctionTool)
        self.assertEqual(result, "3")

    def test_google_style_docstring_parsing(self):
        """
        Test google style docstring parsing
        """

        # given
        @function_tool
        def add_numbers(a: int, b: int):
            """
            add two numbers

            Args:
                a(int): first name
                b(int): second name
            """
            return a + b

        # when
        schema = add_numbers.schema_model(use_profile=True)
        schema_json = schema.model_json_schema()
        flatten_schema_json = flatten_json_schema(schema_json)
        func_schema = flatten_schema_json["properties"]["body"]

        # then
        self.assertTrue(str(func_schema["description"]).startswith("add two numbers"))
        self.assertEqual(func_schema["title"], "add_numbers")
        self.assertEqual(func_schema["required"], ["a", "b"])
        self.assertEqual(func_schema["type"], "object")
        self.assertEqual(func_schema["properties"]["a"]["type"], "integer")
        self.assertEqual(func_schema["properties"]["a"]["description"], "first name")
        self.assertEqual(func_schema["properties"]["b"]["type"], "integer")
        self.assertEqual(func_schema["properties"]["b"]["description"], "second name")

    def test_javadoc_style_docstring_parsing(self):
        """
        Test javadoc style docstring parsing
        """

        # given
        @function_tool
        def add_numbers(a: int, b: int):
            """
            add two numbers

            @param a first name
            @param b second name
            """
            return a + b

        # when
        schema = add_numbers.schema_model(use_profile=True)
        schema_json = schema.model_json_schema()
        flatten_schema_json = flatten_json_schema(schema_json)
        func_schema = flatten_schema_json["properties"]["body"]

        # then
        self.assertTrue(str(func_schema["description"]).startswith("add two numbers"))
        self.assertEqual(func_schema["title"], "add_numbers")
        self.assertEqual(func_schema["required"], ["a", "b"])
        self.assertEqual(func_schema["type"], "object")
        self.assertEqual(func_schema["properties"]["a"]["type"], "integer")
        self.assertEqual(func_schema["properties"]["a"]["description"], "first name")
        self.assertEqual(func_schema["properties"]["b"]["type"], "integer")
        self.assertEqual(func_schema["properties"]["b"]["description"], "second name")

    def test_sphinx_style_docstring_parsing(self):
        """
        Test sphinx style docstring parsing
        """

        # given
        @function_tool
        def add_numbers(a: int, b: int):
            """
            add two numbers

            :param a: first name
            :param b: second name
            """
            return a + b

        # when
        schema = add_numbers.schema_model(use_profile=True)
        schema_json = schema.model_json_schema()
        flatten_schema_json = flatten_json_schema(schema_json)
        func_schema = flatten_schema_json["properties"]["body"]

        # then
        self.assertTrue(str(func_schema["description"]).startswith("add two numbers"))
        self.assertEqual(func_schema["title"], "add_numbers")
        self.assertEqual(func_schema["required"], ["a", "b"])
        self.assertEqual(func_schema["type"], "object")
        self.assertEqual(func_schema["properties"]["a"]["type"], "integer")
        self.assertEqual(func_schema["properties"]["a"]["description"], "first name")
        self.assertEqual(func_schema["properties"]["b"]["type"], "integer")
        self.assertEqual(func_schema["properties"]["b"]["description"], "second name")

    def test_simple_style_docstring_parsing(self):
        """
        Test simple docstring parsing
        """

        # given
        @function_tool
        def add_numbers(a: int, b: int):
            """
            add two numbers

            a: first name
            b(int): second name
            """
            return a + b

        # when
        schema = add_numbers.schema_model(use_profile=True)
        schema_json = schema.model_json_schema()
        flatten_schema_json = flatten_json_schema(schema_json)
        func_schema = flatten_schema_json["properties"]["body"]

        # then
        self.assertTrue(str(func_schema["description"]).startswith("add two numbers"))
        self.assertEqual(func_schema["title"], "add_numbers")
        self.assertEqual(func_schema["required"], ["a", "b"])
        self.assertEqual(func_schema["type"], "object")
        self.assertEqual(func_schema["properties"]["a"]["type"], "integer")
        self.assertEqual(func_schema["properties"]["a"]["description"], "first name")
        self.assertEqual(func_schema["properties"]["b"]["type"], "integer")
        self.assertEqual(func_schema["properties"]["b"]["description"], "second name")
