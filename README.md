# test-renovate-updates

Run Renovate:

`LOG_LEVEL=debug RENOVATE_CONFIG_FILE="$RENOVATE_GLOBAL_CONFIG" renovate --token "$GH_TOKEN" cqi-stonesoup-test/test-renovate-updates 2>&1 >build.log
`

Demo script:

Show pipelines changes for a specific task update.

```bash
python3 migration-tool.py -l run.log \
    -f quay.io/mytestworkload/test-renovate-updates-task-init:0.1@sha256:00e467c83c0188130134e0581bdd1d74fa3657ac1cef96345d92d50f9c96e3b0 \
    -t quay.io/mytestworkload/test-renovate-updates-task-init:0.1@sha256:15e973915b62a11bb916813ffef92968e180513017013ae77e300c5ef3cb4f14
```
