# test-renovate-updates

Task and pipeline bundles build process:

* Modify task or pipeline
* Commit the changes
* `make build/and/push`
* Push

Push is optional and is ok to do before or after the `make`.

Run Renovate:

```bash
export GH_TOKEN=
export TEST_REPO=cqi-stonesoup-test/test-renovate-updates
make run/renovate
```

## Propose a migration

* Modify the pipeline
* Modify the task. Skip if update made to build-definitions is only applied to pipeline.
* Run: `./hack/create-migration.sh <task name>`
* Review the generated migration file
* Commit the working tree

For example, to update execution order of task `coverage`, the workflow is:

- Update field `.runAfter`
- Run `./hack/create-migration.sh coverage`

As a result, task version is bumped in the task definition:

```diff
 metadata:
   name: coverage
   labels:
-    app.kubernetes.io/version: "0.1.2"
+    app.kubernetes.io/version: "0.1.3"
     build.appstudio.redhat.com/build_type: "docker"
   annotations:
```

And, a migration file `tasks/migrations/task-coverage-0.1.3.sh` is generated with yq commands.

The whole changes is in commit [eb8ff062320d1c53e636d50e5a3e9ee119cfb362](https://github.com/cqi-stonesoup-test/test-renovate-updates/commit/eb8ff062320d1c53e636d50e5a3e9ee119cfb362)

The result Renovate update pull request: [PR #42](https://github.com/cqi-stonesoup-test/test-renovate-updates/pull/42/)

## Migrate per task

Example run:

```bash
python3 migration-tool.py \
    -f quay.io/mytestworkload/test-renovate-updates-task-clone:0.1@sha256:059e0bac3ed0877132c31ec201e023eb1e89b49ee1337c2392531e5d59e77809 \
    -t quay.io/mytestworkload/test-renovate-updates-task-clone:0.1@sha256:b4cdb3ea6b1923fa97aa2bff1f5a974910c7c1b7718bb6853e2e78e72811cb1f \
    -m manual \
    -l run5.log \
    -p ./component-a-pipelinerun.yaml
```

It will apply migrations from `./tasks/migrations/task-clone-*.sh`

## Scenarios

Task `init` is selected as the one to be changed for fictional update.

Show pipelines changes for fictional task update and `init` task itself:

```bash
python3 migration-tool.py \
    -f quay.io/mytestworkload/test-renovate-updates-task-init:0.1@sha256:00e467c83c0188130134e0581bdd1d74fa3657ac1cef96345d92d50f9c96e3b0 \
    -t quay.io/mytestworkload/test-renovate-updates-task-init:0.1@sha256:13534468b93b03a01bf78ac9345f5e8c8d2d6d2e65cb11e6431526642e5730ff \
    -l ./run.log \
	-p ./pipelinerun.yaml
```

There are a few updates to `init` task and a fictional update inside which a workspace is added to the pipeline in commit 99a89935a1080c29add1567535b95597137421ad.
