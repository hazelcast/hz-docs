#!/usr/bin/env python3
import unittest
from unittest.mock import patch, MagicMock, call
import os
import json
import subprocess
import logging

import antora_utils

class TestAntoraUtils(unittest.TestCase):

    def test_get_pr_title(self) -> None:
        title = antora_utils.get_pr_title("main", "5.8.0")
        self.assertEqual(title, "Update branch main to 5.8.0")

    @patch("antora_utils.subprocess.run")
    def test_run_command_success(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(stdout="  mock output \n", returncode=0)
        output = antora_utils.run_command(["git", "status"])
        self.assertEqual(output, "mock output")
        mock_run.assert_called_once_with(["git", "status"], capture_output=True, text=True, check=True)

    @patch("antora_utils.subprocess.run")
    def test_run_command_failure(self, mock_run: MagicMock) -> None:
        mock_run.side_effect = subprocess.CalledProcessError(1, ["git", "status"], stderr="mock error")
        with self.assertRaises(RuntimeError):
            antora_utils.run_command(["git", "status"])

    @patch("antora_utils.run_command")
    def test_git_checkout_remote(self, mock_run_command: MagicMock) -> None:
        antora_utils.git_checkout_remote("local-feature", "remote-base")
        expected_calls = [
            call([
                "git", "fetch",
                "origin", "remote-base"
            ]),
            call([
                "git", "checkout",
                "-b", "local-feature",
                "origin/remote-base"
            ])
        ]
        mock_run_command.assert_has_calls(expected_calls)

    @patch("antora_utils.git_checkout_remote")
    @patch("antora_utils.datetime")
    def test_checkout_branch(self, mock_datetime: MagicMock, mock_checkout_remote: MagicMock) -> None:
        mock_datetime.now.return_value = MagicMock(strftime=MagicMock(return_value="29062026105000"))
        
        branch_name = antora_utils.checkout_branch("release", "5.8.0")
        
        self.assertEqual(branch_name, "update_release_5.8.0_29062026105000")
        mock_checkout_remote.assert_called_once_with("update_release_5.8.0_29062026105000", "5.8.0")

    @patch("antora_utils.run_command")
    def test_git_push_remote(self, mock_run_command: MagicMock) -> None:
        antora_utils.git_push_remote("feature-branch")
        mock_run_command.assert_called_once_with([
            "git", "push",
            "origin",
            "feature-branch"
        ])

    @patch("antora_utils.git_push_remote")
    @patch("antora_utils.run_command")
    def test_commit_changes(self, mock_run_command: MagicMock, mock_push_remote: MagicMock) -> None:
        antora_utils.commit_changes("main", "5.8.0", ["docs/antora.yml"], "update_feature_branch")

        expected_calls = [
            call([
                "git", "add",
                "docs/antora.yml"
            ]),
            call([
                "git", "commit",
                "--message", "Update branch main to 5.8.0"
            ])
        ]
        mock_run_command.assert_has_calls(expected_calls)
        mock_push_remote.assert_called_once_with("update_feature_branch")

    @patch.dict(os.environ, {
        "GITHUB_SERVER_URL": "https://github.com",
        "GITHUB_REPOSITORY": "hz-devops-test/hz-docs",
        "GITHUB_RUN_ID": "12345"
    })
    @patch("antora_utils.run_command")
    def test_create_github_pr(self, mock_run_command: MagicMock) -> None:
        antora_utils.create_github_pr("main", "feature-branch", "5.8.0")
        
        mock_run_command.assert_called_once_with([
            "gh", "pr", "create",
            "--title", "Update branch main to 5.8.0",
            "--body", "Triggered by GitHub Action Run: https://github.com/hz-devops-test/hz-docs/actions/runs/12345",
            "--base", "main",
            "--head", "feature-branch"
        ])

    @patch("antora_utils.run_command")
    def test_merge_github_pr_success(self, mock_run_command: MagicMock) -> None:
        mock_prs_json = json.dumps([{"number": 42, "title": "Update branch main to 5.8.0"}])
        mock_run_command.side_effect = [mock_prs_json, ""]
        
        antora_utils.merge_github_pr("main", "5.8.0")

        mock_run_command.assert_has_calls([
            call([
                "gh", "search", "prs",
                "--state", "open",
                "--base", "main",
                "--match", "title", f'"Update branch main to 5.8.0"',
                "--json", "number,title"
            ]),
            call([
                "gh", "pr", "merge", "42",
                "--squash",
                "--admin",
                "--delete-branch"
            ])
        ])

    @patch("antora_utils.run_command")
    def test_merge_github_pr_not_found(self, mock_run_command: MagicMock) -> None:
        mock_run_command.return_value = json.dumps([])
        
        with self.assertRaises(RuntimeError) as context:
            antora_utils.merge_github_pr("main", "5.8.0")
            
        self.assertIn("PR not found", str(context.exception))

    @patch("antora_utils.logger")
    @patch("antora_utils.run_command")
    def test_merge_github_pr_not_found_no_fail(self, mock_run_command: MagicMock, mock_logger: MagicMock) -> None:
        mock_run_command.return_value = json.dumps([])

        antora_utils.merge_github_pr("main", "5.8.0", fail_on_missing=False)

        mock_logger.warning.assert_called_once()
        self.assertEqual(mock_run_command.call_count, 1)

    @patch("antora_utils.run_command")
    def test_merge_github_pr_conflict_multiple(self, mock_run_command: MagicMock) -> None:
        mock_prs_json = json.dumps([
            {"number": 42, "title": "Update branch main to 5.8.0"},
            {"number": 43, "title": "Update branch main to 5.8.0"}
        ])
        mock_run_command.return_value = mock_prs_json
        
        with self.assertRaises(RuntimeError) as context:
            antora_utils.merge_github_pr("main", "5.8.0")
            
        self.assertIn("Conflict: Multiple open PRs found", str(context.exception))

    @patch("logging.basicConfig")
    def test_setup_logger(self, mock_basic_config) -> None:
        import importlib
        import antora_utils

        scenarios = [
            {"env_val": "0", "expected_level": logging.INFO, "level_name": "INFO"},
            {"env_val": "1", "expected_level": logging.DEBUG, "level_name": "DEBUG"}
        ]

        for case in scenarios:
            with self.subTest(level=case["level_name"]):
                mock_basic_config.reset_mock()

                with patch.dict(os.environ, {"RUNNER_DEBUG": case["env_val"]}):
                    importlib.reload(antora_utils)
                    mock_basic_config.assert_called_once()
                    kwargs = mock_basic_config.call_args[1]
                    self.assertEqual(kwargs["level"], case["expected_level"])
                    self.assertIn("[%(levelname)s]", kwargs["format"])

if __name__ == "__main__":
    unittest.main(testRunner=unittest.TextTestRunner(verbosity=2))
