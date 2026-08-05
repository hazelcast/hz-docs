#!/usr/bin/env python3
import logging
from typing import Any
from ruamel.yaml import YAML
from packaging.version import parse
import antora_utils as utils

ANTORA_FILE: str = "docs/antora.yml"

logger: logging.Logger = utils.setup_logger(__name__)

def get_beta_suffix(version: str) -> str:

    parsed = parse(version)
    if parsed.pre and parsed.pre[0] == 'b':
        return f"BETA-{parsed.pre[1]}"
    return ""

def resolve_versions(
    target_version:str,
    rel_major_minor:str,
    master_major_minor:str,
    is_beta_release:bool,
    is_rel_major_minor:bool,
    is_main:bool,
    data:Any
) -> utils.AntoraVersions:

    antora_versions = utils.AntoraVersions()
    attrs = data['asciidoc']['attributes']

    if is_main:
        master_snapshot = f"{master_major_minor}-SNAPSHOT"
        antora_versions.version = f"{master_major_minor}-snapshot"
        antora_versions.display_version = master_snapshot
        antora_versions.minor_version = master_snapshot
        antora_versions.attr_version = master_snapshot
        antora_versions.os_version = target_version
        antora_versions.ee_version = target_version
        antora_versions.full_version = target_version
    elif is_beta_release:
        local_clean = target_version.upper().replace("-SNAPSHOT", "")
        beta_suffix = get_beta_suffix(local_clean)
        mm = rel_major_minor
        antora_versions.version = f"{mm}-{beta_suffix.lower()}"
        antora_versions.display_version = f"{mm}-{beta_suffix}"
        antora_versions.full_version = target_version
        antora_versions.minor_version = f"{mm}-{beta_suffix}"
        antora_versions.attr_version = f"{mm}-{beta_suffix}"
        antora_versions.os_version = attrs.get('os-version')
        antora_versions.ee_version = target_version
        antora_versions.pop_snapshot = False
    else:
        # Patch
        antora_versions.version = rel_major_minor
        antora_versions.display_version = rel_major_minor
        antora_versions.minor_version = rel_major_minor
        antora_versions.attr_version = rel_major_minor
        antora_versions.full_version = target_version
        antora_versions.ee_version = target_version

        if is_rel_major_minor:
            antora_versions.pop_prerelease = True
            antora_versions.pop_snapshot = True

        if not is_rel_major_minor:
            antora_versions.os_version = attrs.get('os-version')
        else:
            antora_versions.os_version = target_version

    return antora_versions

def process_antora(
    target_version:str,
    rel_major_minor:str,
    master_major_minor:str,
    is_beta_release:bool,
    is_rel_major_minor:bool,
    is_main:bool
) -> None:

    # Using https://yaml.dev/doc/ruamel.yaml/
    yaml: YAML = YAML()
    # Preserve original single/double quotess
    yaml.preserve_quotes = True
    # Preserve indentations as per current `antora.yml` layout
    # See https://yaml.dev/doc/ruamel.yaml/detail/#Indentation_of_block_sequences
    yaml.indent(mapping=2, sequence=4, offset=2)
    # Extend line wrapping limit to prevent premature line breaks
    yaml.width = 4096
    
    with open(ANTORA_FILE, 'r+') as f:
        data = yaml.load(f)
        attrs = data['asciidoc']['attributes']

        antora_versions = resolve_versions(
            target_version=target_version,
            rel_major_minor=rel_major_minor,
            master_major_minor=master_major_minor,
            is_beta_release=is_beta_release,
            is_rel_major_minor=is_rel_major_minor,
            is_main=is_main,
            data=data
        )

        data['version'] = antora_versions.version
        data['display_version'] = antora_versions.display_version
        attrs['full-version'] = antora_versions.full_version
        attrs['os-version'] = antora_versions.os_version
        attrs['ee-version'] = antora_versions.ee_version

        if 'minor-version' in attrs or is_main:
            attrs['minor-version'] = antora_versions.minor_version

        if 'version' in attrs or is_main:
            attrs['version'] = antora_versions.attr_version

        if antora_versions.pop_prerelease:
            data.pop('prerelease', None)

        if antora_versions.pop_snapshot:
            attrs.pop('snapshot', None)

        f.seek(0)
        yaml.dump(data, f)
        f.truncate()

def update_release(
    release_ver:str,
    rel_major_minor:str,
    master_major_minor:str,
    is_beta_release:bool,
    is_rel_major_minor:bool,
    is_patch_release:bool
) -> None:

    # For PATCH release, checkout v/branch directly. When release is MAJOR/MINOR or BETA,
    # use release branch instead, and v/branch is created from release branch during `promote`
    # phase. This is necessary to prevent premature docs 'live' publishing via v/branch (website
    # auto publishes from v/branch)
    if is_patch_release:
        target_base = f"v/{rel_major_minor}"
    else:
        target_base = release_ver

    update_branch: str = utils.checkout_branch("antora", target_base)
    
    process_antora(
        target_version=release_ver,
        rel_major_minor=rel_major_minor,
        master_major_minor=master_major_minor,
        is_beta_release=is_beta_release,
        is_rel_major_minor=is_rel_major_minor,
        is_main=False
    )
    
    utils.commit_changes(target_base, release_ver, [ANTORA_FILE], update_branch)
    utils.create_github_pr(target_base, update_branch, release_ver)

def update_main(
    master_version:str,
    rel_major_minor:str,
    master_major_minor:str,
    is_rel_major_minor:bool
) -> None:

    target_base: str = "main"
    update_branch: str = utils.checkout_branch("antora", target_base)
    
    process_antora(
        target_version=master_version,
        rel_major_minor=rel_major_minor,
        master_major_minor=master_major_minor,
        is_beta_release=False,
        is_rel_major_minor=is_rel_major_minor,
        is_main=True
    )
    
    utils.commit_changes(target_base, master_version, [ANTORA_FILE], update_branch)
    utils.create_github_pr(target_base, update_branch, master_version)

def update(
    release_ver:str,
    rel_major_minor:str,
    master_version:str,
    master_major_minor:str,
    is_latest_stable_release:str,
    is_beta_release:str,
    is_rel_major_minor:str,
    is_patch_release:str
) -> None:

    is_patch: bool = is_patch_release == "true"
    is_beta: bool = is_beta_release == "true"
    is_rel_mm: bool = is_rel_major_minor == "true"
    is_latest_stable: bool = is_latest_stable_release == "true"

    if is_rel_mm and is_latest_stable:
        update_main(
            master_version=master_version,
            rel_major_minor=rel_major_minor,
            master_major_minor=master_major_minor,
            is_rel_major_minor=is_rel_mm
        )

    update_release(
        release_ver=release_ver,
        rel_major_minor=rel_major_minor,
        master_major_minor=master_major_minor,
        is_beta_release=is_beta,
        is_rel_major_minor=is_rel_mm,
        is_patch_release=is_patch
    )

def merge_pull_requests(
    is_rel_major_minor:str,
    is_patch_release:str,
    release_version:str,
    master_version:str,
    rel_major_minor:str
) -> None:

    is_maj_min: bool = is_rel_major_minor == "true"
    is_patch: bool = is_patch_release == "true"

    if is_maj_min:
        utils.merge_github_pr("main", master_version)

    if is_patch:
        base_branch = f"v/{rel_major_minor}"
    else:
        base_branch = release_version

    utils.merge_github_pr(base_branch, release_version)

def create_v_branch(
    release_version:str,
    rel_major_minor:str,
    is_beta_release:str,
    is_patch_release:str
) -> None:

    is_patch: bool = is_patch_release == "true"
    is_beta: bool = is_beta_release == "true"

    # Patch `v/branch` should already exist so skip
    if is_patch:
        return

    v_branch_name = f"v/{rel_major_minor}"

    if is_beta:
        beta_suffix = get_beta_suffix(release_version)
        v_branch_name = f"v/{rel_major_minor}-{beta_suffix}"

    utils.git_checkout_remote(v_branch_name, release_version)
    utils.git_push_remote(v_branch_name)
