
import os
import os.path


def migrate(from_task_bundle: str, to_task_bundle: str) -> None:
    """Apply migrations between the updated task bundles

    Not every task bundle update has migration. Discover possible migration with
    the version set in label app.kubernetes.io/version and apply the migrations
    by executing the migration script.

    If no migration is discovered with the version, skip it.
    """

    # step: determine the task bundles update range

    # step: find migration script file for each task bundle update
    #       according to the version, which can be read from the label version of bundle image

    # step: resolve the pipeline

    # step: apply the migration scripts

    # step: save the pipeline
    #       if it is a standalone pipeline file, write it to the file
    #       if it is extracted from .spec.pipelineSpec, inject it back and save the original file

