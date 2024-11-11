#!/usr/bin/python3

import argparse
import logging
import os
import re
import tempfile
import tarfile
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from utils import ImageReference, parse_image_reference, quay_list_repo_tags, tkn_bundle_fetch, TASK_TAG_REGEXP

import migrate

PIPELINE_BUNDLE_REPO: Final = "quay.io/mytestworkload/test-renovate-updates-pipeline"

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger("migrate")

build_log = logging.getLogger("build.log")
build_log.setLevel(logging.DEBUG)


@dataclass
class PipelineEvent:
    bundle: str
    file_path: str


def find_pipeline(task_bundle: ImageReference) -> str:
    """Find pipeline that contains the given task bundle"""
    if not task_bundle.tag:
        raise ValueError("Tag is empty. Requiring a tag in form version-revision, e.g. 0.1-12345")
    _, revision = task_bundle.tag.rsplit("-", 1)
    return f"{PIPELINE_BUNDLE_REPO}:{revision}"


def fetch_pipeline_from_bundle(bundle: str, dest_dir: str) -> str:
    pipeline_name: Final = "pipeline-build"
    image_ref = parse_image_reference(bundle)
    pipeline_file = Path(dest_dir, f"{pipeline_name}-{image_ref.tag}.yaml")
    fd, temp_blob_file = tempfile.mkstemp()
    os.close(fd)
    try:
        with open(temp_blob_file, "wb") as f:
            tkn_bundle_fetch(image_ref, f)
        with tarfile.open(temp_blob_file, "r") as tar:
            members = tar.getmembers()
            if len(members) > 1:
                raise ValueError(f"Multiple members in pipeline bundle {bundle}")
            reader = tar.extractfile(members[0])
            if reader is None:
                raise ValueError(f"Member {members[0].name} is not a regular file.")
            pl_content = reader.read().decode("utf-8")
            pipeline_file.write_text(pl_content)
    finally:
        os.unlink(temp_blob_file)
    return str(pipeline_file)


def map_task_bundle_to_pipeline_bundle(task_bundle: str) -> str:
    """Map task bundle to pipeline bundle which includes the task"""
    image_ref: Final = parse_image_reference(task_bundle)
    pipeline_bundle: Final = find_pipeline(image_ref)
    build_log.info("found pipeline bundle: %s", pipeline_bundle)
    return pipeline_bundle


def task_update_history(from_task_bundle: str, to_task_bundle: str) -> list[ImageReference]:
    """Generate task bundle history from the newest to the oldest one"""
    task_bundles_history: list[ImageReference] = []
    append = task_bundles_history.append
    from_image_ref = parse_image_reference(from_task_bundle)
    to_image_ref = parse_image_reference(to_task_bundle)
    in_range = False
    for tag in quay_list_repo_tags(from_image_ref.repository):
        if not re.match(TASK_TAG_REGEXP, tag["name"]):
            continue
        if tag["manifest_digest"] == to_image_ref.digest:
            append(
                ImageReference(
                    registry=to_image_ref.registry,
                    repository=to_image_ref.repository,
                    tag=tag["name"],
                    digest=to_image_ref.digest,
                ),
            )
            in_range = True
        elif tag["manifest_digest"] == from_image_ref.digest:
            append(
                ImageReference(
                    registry=from_image_ref.registry,
                    repository=from_image_ref.repository,
                    tag=tag["name"],
                    digest=from_image_ref.digest,
                )
            )
            break
        elif in_range:
            append(
                ImageReference(
                    registry=from_image_ref.registry,
                    repository=from_image_ref.repository,
                    tag=tag["name"],
                    digest=tag["manifest_digest"],
                ),
            )
    return task_bundles_history


def pipeline_history(from_task_bundle: str, to_task_bundle: str, store_dir: str) -> list[PipelineEvent]:
    """Generate pipeline history from the newest to the oldest one"""
    task_bundles_history = task_update_history(from_task_bundle, to_task_bundle)
    history: list[PipelineEvent] = []
    for task_bundle in task_bundles_history:
        logger.debug("find pipeline for task bundle: %s", task_bundle)
        pipeline_bundle = find_pipeline(task_bundle)
        pipeline_file = fetch_pipeline_from_bundle(pipeline_bundle, store_dir)
        logger.debug("task bundle %s is included in pipelne %s", task_bundle, pipeline_file)
        history.append(PipelineEvent(bundle=pipeline_bundle, file_path=pipeline_file))
    return history


def compare_pipelines(from_pipeline: str, to_pipeline: str) -> str:
    """Compare two pipelines"""
    compare_cmd = [
        "dyff",
        "between",
        "--omit-header",
        "--detect-kubernetes",
        "--no-table-style",
        "--exclude-regexp",
        "/spec/tasks/name=.+/taskRef/params/name=.+/value",
        from_pipeline,
        to_pipeline,
    ]
    proc = subprocess.run(compare_cmd, check=True, capture_output=True, text=True)
    return proc.stdout


def migrate_update(from_task_bundle: str, to_task_bundle: str, defs_temp_dir: str, pipeline_run_file: str = "") -> None:
    # FIXME: all supported pipelines must be handled.
    #
    # Currently, there is no way to know which supported pipeline is based on,
    # unless the oci-ta pipelines because of task name has suffix -oci-ta.
    #
    # So, the process would be:
    # 1. fetch update history for each supported pipeline, e.g. docker-build, docker-build-oci-ta
    # 2. select the pipeline if it includes the current updated task
    events = pipeline_history(from_task_bundle, to_task_bundle, defs_temp_dir)

    history_len = len(events)
    if history_len < 2:
        return
    from_idx = history_len - 1
    while from_idx > 0:
        from_event = events[from_idx]
        to_event = events[from_idx - 1]
        diff = compare_pipelines(from_event.file_path, to_event.file_path)
        if diff == "\n":
            build_log.info(
                "changes from pipeline %s to pipeline%s: no change except task bundle update",
                from_event.bundle,
                to_event.bundle,
            )
        else:
            build_log.info("changes from pipeline %s to pipeline%s:\n%s", from_event.bundle, to_event.bundle, diff)
            if pipeline_run_file:
                migrate.migrate_with_dsl(migrate.generate_dsl(migrate.convert_difference(diff)), pipeline_run_file)
        from_idx -= 1


def main():
    parser = argparse.ArgumentParser(description="Konflux Pipeline Migration Tool")
    parser.add_argument("-f", "--from-task-bundle", required=True, metavar="IMAGE_REF")
    parser.add_argument("-t", "--to-task-bundle", required=True, metavar="IMAGE_REF")
    parser.add_argument(
        "-p",
        "--pipeline-run",
        metavar="PATH",
        dest="pipeline_run_file",
        default="",
        help="Update pipeline for this PipelineRun.",
    )
    parser.add_argument(
        "-m",
        "--migration-mode",
        choices=("auto", "manual"),
        metavar="migration_mode",
        required=True,
        help="Select the migration mode. Mode auto will try to detect the migrations automatically. "
        "Mode manual will discover migration scripts written by developers and apply them one by one",
    )

    args = parser.parse_args()

    from_task_bundle = args.from_task_bundle
    to_task_bundle = args.to_task_bundle

    if from_task_bundle == to_task_bundle:
        logger.info("same task bundles are specified.")
        return

    from_ref = parse_image_reference(from_task_bundle)
    to_ref = parse_image_reference(to_task_bundle)

    if from_ref.qualified_repository != to_ref.qualified_repository:
        logger.error("Given task bundles are not same image.")
        return

    build_log.info("Doing migration for task update:")
    build_log.info("from: %s", args.from_task_bundle)
    build_log.info("to: %s", args.to_task_bundle)

    build_log.debug("inspect image: %s", args.to_task_bundle)

    if args.migration_mode == "manual":
        import migrate_per_task

        migrate_per_task.migrate(args.from_task_bundle, args.to_task_bundle, args.pipeline_run_file)
    else:
        # find out the corresponding pipeline bundle

        defs_temp_dir = os.path.join(os.getcwd(), "pipelines", "temp")
        if not os.path.exists(defs_temp_dir):
            os.makedirs(os.path.join("pipelines", "temp"))

        migrate_update(args.from_task_bundle, args.to_task_bundle, defs_temp_dir, args.pipeline_run_file)


def main_handle_upgrades_json():
    import sys
    import json
    upgrads_json = sys.argv[1]
    n_upgrades = len(json.loads(upgrads_json))
    print(f"There are {n_upgrades} upgrades.")


if __name__ == "__main__":
    main_handle_upgrades_json()
