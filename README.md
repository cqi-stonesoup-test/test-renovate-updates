# test-renovate-updates

Run Renovate:

```bash
export LOG_LEVEL=debug
export RENOVATE_CONFIG_FILE="$RENOVATE_GLOBAL_CONFIG"
export TEST_REPO=cqi-stonesoup-test/test-renovate-updates
renovate --token "$GH_TOKEN" "$TEST_REPO" 2>&1 >renovate.log
```

## scenarios

Show pipelines changes for fictional task update and `init` task itself:

```bash
python3 migration-tool.py -l run.log \
    -f quay.io/mytestworkload/test-renovate-updates-task-init:0.1@sha256:00e467c83c0188130134e0581bdd1d74fa3657ac1cef96345d92d50f9c96e3b0 \
	-t quay.io/mytestworkload/test-renovate-updates-task-init:0.1@sha256:13534468b93b03a01bf78ac9345f5e8c8d2d6d2e65cb11e6431526642e5730ff
```
