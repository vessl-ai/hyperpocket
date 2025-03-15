import unittest

from hyperdock_container.dock import ContainerDock


class TestContainerDock(unittest.TestCase):
    def test_load_from_github(self):
        # given
        dock = ContainerDock()
        github_url = "https://github.com/vessl-ai/hyperpocket/tree/main/tools/none/simple-echo-tool"

        # when
        dock_arguments = dock.load(github_url, dock_vars={"TEST_VARS": "TEST"},
                                   runtime_arguments={"TEST_RUNTIME_ARGS": "TEST"})

        # then
        self.assertEqual(dock_arguments.tool_source, "github")
        self.assertEqual(dock_arguments.request_tool_path,
                         "https://github.com/vessl-ai/hyperpocket/tree/main/tools/none/simple-echo-tool")
        self.assertTrue(dock_arguments.tool_path.exists())
        self.assertEqual(dock_arguments.tool_vars["TEST_VARS"], "TEST")
        self.assertEqual(dock_arguments.runtime_arguments["TEST_RUNTIME_ARGS"], "TEST")

    def test_build(self):
        # given
        dock = ContainerDock()
        github_url = "https://github.com/vessl-ai/hyperpocket/tree/main/tools/none/simple-echo-tool"
        dock_arguments = dock.load(github_url)

        # when
        image_name = dock.build(dock_arguments)
        image = dock.runtime.list_image(image_name)

        # then
        self.assertEqual(len(image), 1)

    def test_dock(self):
        # given
        github_url = "https://github.com/vessl-ai/hyperpocket/tree/main/tools/none/simple-echo-tool"
        dock = ContainerDock()

        # when
        tool = dock.dock(github_url)
        result = tool.invoke(body={"text": "test"}, envs={})

        # then
        self.assertTrue("echo message : test" in result)
