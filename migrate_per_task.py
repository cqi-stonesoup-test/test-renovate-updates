import io
import json
import logging
import os
import os.path
import subprocess
import tempfile

from collections.abc import Generator
from contextlib import contextmanager
from typing import Final

from utils import determine_task_bundle_updates_range, quay_registry, parse_image_reference, load_yaml, dump_yaml

TEKTON_KIND_PIPELINE: Final = "Pipeline"
TEKTON_KIND_PIPELINE_RUN: Final = "PipelineRun"

logger = logging.getLogger("migrate_per_task")
logger.setLevel(logging.DEBUG)


@contextmanager
def resolve_pipeline(pipeline_file: str) -> Generator[str]:
    """Yield resolved pipeline file"""
    origin_pipeline = load_yaml(pipeline_file)

    # TODO: delete the temporary pipeline file?
    # TODO: extract this pipeline resolution

    kind = origin_pipeline["kind"]
    if kind == TEKTON_KIND_PIPELINE:
        yield pipeline_file
    elif kind == TEKTON_KIND_PIPELINE_RUN:
        if "pipelineSpec" in origin_pipeline["spec"]:
            # pipeline definition is inline the PipelineRun
            fd, temp_pipeline_file = tempfile.mkstemp()
            os.close(fd)
            pipeline = {"spec": origin_pipeline["spec"]["pipelineSpec"]}
            dump_yaml(temp_pipeline_file, pipeline)
            yield temp_pipeline_file
            modified_pipeline = load_yaml(temp_pipeline_file)
            origin_pipeline["spec"]["pipelineSpec"] = modified_pipeline["spec"]
            dump_yaml(pipeline_file, origin_pipeline)
        elif "pipelineRef" in origin_pipeline["spec"]:
            # pipeline definition is referenced by name or git-resolver
            pipeline_ref = origin_pipeline["spec"]["pipelineRef"]
            if "name" in pipeline_ref:
                ref_pipeline = os.path.join(os.path.dirname(pipeline_file), pipeline_ref["name"])
                yield ref_pipeline
            elif "bundle" in pipeline_ref:
                # TODO: resolve and read pipeline
                raise NotImplementedError("read pipeline referenced by git-resolver")
            else:
                raise ValueError("Unknown pipelineRef section")
        else:
            raise ValueError("PipelineRun .spec field includes neither .pipelineSpec nor .pipelineRef field.")


def migrate(from_task_bundle: str, to_task_bundle: str, pipeline_run_file: str) -> None:
    """Apply migrations between the updated task bundles

    Not every task bundle update has migration. Discover possible migration with
    the version set in label app.kubernetes.io/version and apply the migrations
    by executing the migration script.

    If no migration is discovered with the version, skip it.
    """

    # step: determine the task bundles update range
    task_bundles_updates_range = determine_task_bundle_updates_range(from_task_bundle, to_task_bundle)

    from_bundle_ref = parse_image_reference(from_task_bundle)

    # step: find migration script file for each task bundle update
    #       according to the version, which can be read from the label version of bundle image
    migration_files: list[str] = []
    for tag in reversed(task_bundles_updates_range):
        image_digest = tag["manifest_digest"]
        manifest = quay_registry.get_manifest(from_bundle_ref.repository, image_digest)

        layers = manifest["layers"]
        if len(layers) > 1:
            raise ValueError(f"Task bundle @{image_digest} should have a single layer per task.")
        task_name = layers[0]["annotations"]["dev.tekton.image.name"]

        config_digest = manifest["config"]["digest"]
        buf = io.BytesIO()
        quay_registry.fetch_blob(from_bundle_ref.repository, config_digest, buf)
        config_json = json.loads(buf.getvalue())
        buf.close()
        task_version = config_json["config"]["Labels"]["version"]

        # NOTE:
        # for demo, discovering the migration scripts from local filesystem
        # for real implementation, it must be resolved from the build-definitions repository via network.

        migration_file = f"./tasks/migrations/task-{task_name}-{task_version}.sh"
        if os.path.exists(migration_file):
            logger.info("discovered migration file %s", migration_file)
            migration_files.append(migration_file)

    # step: apply the migration scripts
    with resolve_pipeline(pipeline_run_file) as pipeline_file:
        for migration_file in migration_files:
            logger.info("apply migrations %s to %s", migration_file, pipeline_file)
            subprocess.run(["bash", migration_file, pipeline_file], check=True)
