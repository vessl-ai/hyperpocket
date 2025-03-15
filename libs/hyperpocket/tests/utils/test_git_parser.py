import unittest
from unittest.mock import patch, MagicMock

from hyperpocket.util.git_parser import GitParser


class TestGitParser(unittest.TestCase):
    def test_parse_github_repo_url_main(self):
        """
        Test Parsing github main repo url.
        """
        # given
        github_url = "https://github.com/vessl-ai/hyperpocket"

        # when
        repo_url, branch, directory_path, git_sha = GitParser.parse_repo_url(github_url)

        # then

        self.assertEqual(repo_url, "https://github.com/vessl-ai/hyperpocket")
        self.assertEqual(branch, "HEAD")
        self.assertEqual(directory_path, "")
        self.assertIsNotNone(git_sha)

    def test_parse_github_repo_url_specific_path(self):
        """
        Test Parsing github main repo url.
        """
        # given
        github_url = "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/get-messages"

        # when
        repo_url, branch, directory_path, git_sha = GitParser.parse_repo_url(github_url)

        # then

        self.assertEqual(repo_url, "https://github.com/vessl-ai/hyperpocket")
        self.assertEqual(branch, "main")
        self.assertEqual(directory_path, "tools/slack/get-messages")
        self.assertIsNotNone(git_sha)

    def test_parse_non_github_repo_url(self):
        """
        Test Parsing non-github repo url.
        It should raise error.
        """
        # given
        non_github_url = "https://bitbucket.org/vessl-ai/hyperpocket"

        # when / then
        with self.assertRaises(AttributeError):
            GitParser.parse_repo_url(non_github_url)

    @patch('hyperpocket.util.git_parser.GitParser.git_branches_cache', new_callable=dict)
    @patch('git.cmd.Git')
    def test_get_git_branches_uses_cache(self, mock_git, mock_cache):
        """
        Test that get_git_branches uses cache after the first call.
        """
        # given
        repo_url = "https://github.com/vessl-ai/hyperpocket"

        # Mock the ls_remote method on the Git instance
        mock_git_instance = mock_git.return_value
        mock_git_instance.ls_remote.return_value = "abc123\tHEAD\nxyz789\trefs/heads/main"

        # Ensure the cache is empty before the first call
        mock_cache.clear()

        # when
        branches_first_call = GitParser.get_git_branches(repo_url)
        branches_second_call = GitParser.get_git_branches(repo_url)

        # Ensure the branches are correctly parsed
        expected_branches = {
            "HEAD": "abc123",
            "main": "xyz789"
        }
        self.assertEqual(branches_first_call, expected_branches)
        self.assertEqual(branches_second_call, expected_branches)

        # Check that ls_remote was called only once
        mock_git_instance.ls_remote.assert_called_once_with(repo_url)

        # Check that the cache was accessed
        self.assertIn(repo_url, mock_cache)
