#!/usr/bin/env python3
import os
import sys
import unittest
from unittest.mock import patch, call
from ruamel.yaml import YAML

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import antora_updater as antora

class DynamicFileSimulator:
    """
    Virtual filesystem router that isolates sequential file access.
    Prevents standard mock_open data cross-contamination when update_main 
    and update_release run in the same process.
    """
    def __init__(self, initial_content: str):
        self.content = initial_content
        self.history = []

    def open_stream(self, file_path: str, mode: str):
        return VirtualFileContext(self, mode)

class VirtualFileContext:
    """
    Simulates text/binary file stream behaviors.
    Delivers EOF empty strings on consecutive reads to prevent infinite YAML 
    loops, transparently decodes raw bytes, and commits writes on block exit.
    Supports seek and truncate operations for r+ block mode scopes.
    """
    def __init__(self, factory: DynamicFileSimulator, mode: str):
        self.factory = factory
        self.mode = mode
        self.read_done = False
        self.local_buffer = []

    def read(self, *args, **kwargs) -> str:
        if ("r" in self.mode or "+" in self.mode) and not self.read_done:
            self.read_done = True
            return self.factory.content
        return ""

    def write(self, data) -> int:
        text_chunk = data.decode("utf-8") if isinstance(data, bytes) else data
        self.local_buffer.append(text_chunk)
        return len(data)

    def seek(self, position: int, *args, **kwargs) -> None:
        if position == 0:
            self.local_buffer = []

    def truncate(self, *args, **kwargs) -> None:
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if ("w" in self.mode or "+" in self.mode) and self.local_buffer:
            completed_doc = "".join(self.local_buffer)
            self.factory.content = completed_doc
            self.factory.history.append(completed_doc)


class TestAntoraUpdater(unittest.TestCase):

    def setUp(self) -> None:
        self.yaml: YAML = YAML()
        self.yaml.preserve_quotes = True

    def get_main_template(self) -> str:
        return """name: hazelcast
title: Hazelcast Platform
version: '5.8-snapshot'
display_version: '5.8-SNAPSHOT'
prerelease: true
snapshot: true
asciidoc:
  attributes:
    full-version: '5.8.0-SNAPSHOT'
    os-version: '5.8.0-SNAPSHOT'
    ee-version: '5.8.0-SNAPSHOT'
    hz-repo-swagger-branch: 'master'
    jet-version: '4.5.4'
    minor-version: '5.8-SNAPSHOT'
    version: '5.8-SNAPSHOT'    
    experimental: true
    snapshot: true
    page-toclevels: 1
nav:
  - modules/ROOT/nav.adoc
"""

    def get_release_patch_template(self) -> str:
        return """name: hazelcast
title: Hazelcast Platform
version: '5.8'
display_version: '5.8'
asciidoc:
  attributes:
    full-version: '5.8.0'
    os-version: '5.8.0'
    ee-version: '5.8.0'
    hz-repo-swagger-branch: 'master'
    jet-version: '4.5.4'
    minor-version: '5.8'
    version: '5.8'    
    experimental: true
    page-toclevels: 1
nav:
  - modules/ROOT/nav.adoc
"""

    def assert_untouched_properties(self, data: dict) -> None:
        attrs = data["asciidoc"]["attributes"]
        self.assertEqual(attrs["hz-repo-swagger-branch"], "master")
        self.assertEqual(attrs["jet-version"], "4.5.4")
        self.assertTrue(attrs["experimental"])

    @patch("builtins.open")
    @patch("antora_utils.checkout_branch")
    @patch("antora_utils.commit_changes")
    @patch("antora_utils.create_github_pr")
    def test_scenario_1_major_minor_main_flow(self, mock_pr, mock_commit, mock_checkout, mock_open, *args) -> None:
        simulator = DynamicFileSimulator(self.get_main_template())
        mock_open.side_effect = simulator.open_stream
        mock_checkout.return_value = "update_mock_branch_123"

        antora.update(
            release_ver="5.8.0",
            rel_major_minor="5.9",
            master_version="5.9.0-SNAPSHOT",
            master_major_minor="5.9",
            is_latest_stable_release="true",
            is_beta_release="false",
            is_rel_major_minor="true",
            is_patch_release="false"
        )
        
        self.assertEqual(len(simulator.history), 2)
        mock_checkout.assert_any_call("antora", "main")
        mock_checkout.assert_any_call("antora", "5.8.0")
        
        main_data = self.yaml.load(simulator.history[0])
        release_data = self.yaml.load(simulator.history[1])

        self.assertEqual(main_data["asciidoc"]["attributes"]["full-version"], "5.9.0-SNAPSHOT")
        self.assertEqual(main_data["asciidoc"]["attributes"]["snapshot"], True)
        self.assert_untouched_properties(main_data)

        self.assertEqual(release_data["asciidoc"]["attributes"]["full-version"], "5.8.0")
        self.assertNotIn("snapshot", release_data["asciidoc"]["attributes"])
        self.assert_untouched_properties(release_data)

    @patch("builtins.open")
    @patch("antora_utils.checkout_branch")
    @patch("antora_utils.commit_changes")
    @patch("antora_utils.create_github_pr")
    def test_scenario_2_major_minor_release_flow(self, mock_pr, mock_commit, mock_checkout, mock_open, *args) -> None:
        simulator = DynamicFileSimulator(self.get_main_template())
        mock_open.side_effect = simulator.open_stream
        mock_checkout.return_value = "update_mock_branch_123"

        antora.update(
            release_ver="5.8.0",
            rel_major_minor="5.9",
            master_version="5.9.0-SNAPSHOT",
            master_major_minor="5.9",
            is_latest_stable_release="true",
            is_beta_release="false",
            is_rel_major_minor="true",
            is_patch_release="false"
        )
        
        self.assertEqual(len(simulator.history), 2)
        main_data = self.yaml.load(simulator.history[0])
        release_data = self.yaml.load(simulator.history[1])
        
        self.assertEqual(main_data["asciidoc"]["attributes"]["full-version"], "5.9.0-SNAPSHOT")
        self.assertEqual(release_data["asciidoc"]["attributes"]["full-version"], "5.8.0")
        self.assertNotIn("snapshot", release_data["asciidoc"]["attributes"])
        self.assert_untouched_properties(release_data)

    @patch("builtins.open")
    @patch("antora_utils.checkout_branch")
    @patch("antora_utils.commit_changes")
    @patch("antora_utils.create_github_pr")
    def test_scenario_3_beta_prerelease_flow(self, mock_pr, mock_commit, mock_checkout, mock_open, *args) -> None:
        simulator = DynamicFileSimulator(self.get_main_template())
        mock_open.side_effect = simulator.open_stream
        mock_checkout.return_value = "update_mock_branch_123"

        antora.update(
            release_ver="5.8.0-BETA-1",
            rel_major_minor="5.8",
            master_version="5.8.0-SNAPSHOT",
            master_major_minor="5.8",
            is_latest_stable_release="false",
            is_beta_release="true",
            is_rel_major_minor="true",
            is_patch_release="false"
        )
        
        mock_checkout.assert_called_once_with("antora", "5.8.0-BETA-1")
        self.assertEqual(len(simulator.history), 1)
        beta_data = self.yaml.load(simulator.history[-1])
        self.assertEqual(beta_data["version"], "5.8-beta-1")
        self.assertEqual(beta_data["display_version"], "5.8-BETA-1")
        self.assertEqual(beta_data["asciidoc"]["attributes"]["full-version"], "5.8.0-BETA-1")
        self.assertEqual(beta_data["asciidoc"]["attributes"]["os-version"], "5.8.0-SNAPSHOT")
        self.assertEqual(beta_data["asciidoc"]["attributes"]["ee-version"], "5.8.0-BETA-1")
        self.assertEqual(beta_data["asciidoc"]["attributes"]["minor-version"], "5.8-BETA-1")
        self.assertEqual(beta_data["asciidoc"]["attributes"]["version"], "5.8-BETA-1")
        self.assert_untouched_properties(beta_data)

    @patch("builtins.open")
    @patch("antora_utils.checkout_branch")
    @patch("antora_utils.commit_changes")
    @patch("antora_utils.create_github_pr")
    def test_scenario_4_patch_latest_flow(self, mock_pr, mock_commit, mock_checkout, mock_open, *args) -> None:
        simulator = DynamicFileSimulator(self.get_release_patch_template())
        mock_open.side_effect = simulator.open_stream
        mock_checkout.return_value = "update_mock_branch_123"

        antora.update(
            release_ver="5.8.1",
            rel_major_minor="5.8",
            master_version="5.9.0-SNAPSHOT",
            master_major_minor="5.9",
            is_latest_stable_release="true",
            is_beta_release="false",
            is_rel_major_minor="false",
            is_patch_release="true"
        )
        
        mock_checkout.assert_called_once_with("antora", "v/5.8")
        self.assertEqual(len(simulator.history), 1)
        patch_data = self.yaml.load(simulator.history[-1])
        self.assertEqual(patch_data["asciidoc"]["attributes"]["full-version"], "5.8.1")
        self.assertEqual(patch_data["asciidoc"]["attributes"]["os-version"], "5.8.0")
        self.assert_untouched_properties(patch_data)

    @patch("builtins.open")
    @patch("antora_utils.checkout_branch")
    @patch("antora_utils.commit_changes")
    @patch("antora_utils.create_github_pr")
    def test_scenario_5_patch_not_latest_flow(self, mock_pr, mock_commit, mock_checkout, mock_open, *args) -> None:
        simulator = DynamicFileSimulator(self.get_release_patch_template())
        mock_open.side_effect = simulator.open_stream
        mock_checkout.return_value = "update_mock_branch_123"

        antora.update(
            release_ver="5.8.1",
            rel_major_minor="5.8",
            master_version="5.9.0-SNAPSHOT",
            master_major_minor="5.9",
            is_latest_stable_release="false",
            is_beta_release="false",
            is_rel_major_minor="false",
            is_patch_release="true"
        )
        
        mock_checkout.assert_called_once_with("antora", "v/5.8")
        self.assertEqual(len(simulator.history), 1)
        patch_data = self.yaml.load(simulator.history[-1])
        self.assertEqual(patch_data["asciidoc"]["attributes"]["full-version"], "5.8.1")
        self.assertEqual(patch_data["asciidoc"]["attributes"]["os-version"], "5.8.0")
        self.assert_untouched_properties(patch_data)

    @patch("antora_utils.merge_github_pr")
    def test_merge_pull_requests_major_minor(self, mock_merge) -> None:
        antora.merge_pull_requests(
            is_rel_major_minor="true",
            is_patch_release="false",
            release_version="5.8.0",
            master_version="5.9.0-SNAPSHOT",
            rel_major_minor="5.8"
        )
        mock_merge.assert_has_calls([
            call("main", "5.9.0-SNAPSHOT"),
            call("5.8.0", "5.8.0")
        ])

    @patch("antora_utils.merge_github_pr")
    def test_merge_pull_requests_beta(self, mock_merge) -> None:
        antora.merge_pull_requests(
            is_rel_major_minor="false", 
            is_patch_release="false",
            release_version="5.8.0-BETA-1",
            master_version="5.8.0-SNAPSHOT",
            rel_major_minor="5.8"
        )
        mock_merge.assert_called_once_with("5.8.0-BETA-1", "5.8.0-BETA-1")

    @patch("antora_utils.merge_github_pr")
    def test_merge_pull_requests_patch(self, mock_merge) -> None:
        antora.merge_pull_requests(
            is_rel_major_minor="false",
            is_patch_release="true",
            release_version="5.8.1",
            master_version="5.9.0-SNAPSHOT",
            rel_major_minor="5.8"
        )
        mock_merge.assert_called_once_with("v/5.8", "5.8.1")

    @patch("antora_utils.git_push_remote")
    @patch("antora_utils.git_checkout_remote")
    def test_create_v_branch_standard(self, mock_checkout, mock_push) -> None:
        antora.create_v_branch(
            release_version="5.8.0",
            rel_major_minor="5.8",
            is_beta_release="false",
            is_patch_release="false"
        )
        mock_checkout.assert_called_once_with("v/5.8", "5.8.0")
        mock_push.assert_called_once_with("v/5.8")

    @patch("antora_utils.git_push_remote")
    @patch("antora_utils.git_checkout_remote")
    def test_create_v_branch_beta(self, mock_checkout, mock_push) -> None:
        antora.create_v_branch(
            release_version="5.8.0-BETA-1",
            rel_major_minor="5.8",
            is_beta_release="true",
            is_patch_release="false"
        )
        mock_checkout.assert_called_once_with("v/5.8-BETA-1", "5.8.0-BETA-1")
        mock_push.assert_called_once_with("v/5.8-BETA-1")

    @patch("antora_utils.git_push_remote")
    @patch("antora_utils.git_checkout_remote")
    def test_create_v_branch_patch(self, mock_checkout, mock_push) -> None:
        antora.create_v_branch(
            release_version="5.8.1",
            rel_major_minor="5.8",
            is_beta_release="false",
            is_patch_release="true"
        )
        mock_checkout.assert_not_called()
        mock_push.assert_not_called()

if __name__ == "__main__":
    unittest.main(testRunner=unittest.TextTestRunner(verbosity=2))
