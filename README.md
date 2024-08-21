# test-renovate-updates

Run Renovate:

`LOG_LEVEL=debug RENOVATE_CONFIG_FILE="$RENOVATE_GLOBAL_CONFIG" renovate --token "$GH_TOKEN" cqi-stonesoup-test/test-renovate-updates 2>&1 >build.log
`

diff --git a/Containerfile.utils b/Containerfile.utils
index a5b4289..5bb2dc3 100644
--- a/Containerfile.utils
+++ b/Containerfile.utils
@@ -1,4 +1,4 @@
-FROM registry.fedoraproject.org/fedora-minimal:40
+FROM registry.fedoraproject.org/fedora-minimal:42
 ARG version=latest
 LABEL \
     org.opencontainers.image.title="utils image for testing renovate update PRs" \
diff --git a/README.md b/README.md
index dc3f096..e61d4b9 100644
--- a/README.md
+++ b/README.md
@@ -4,3 +4,4 @@ Run Renovate:
 
 `LOG_LEVEL=debug RENOVATE_CONFIG_FILE="$RENOVATE_GLOBAL_CONFIG" renovate --token "$GH_TOKEN" cqi-stonesoup-test/test-renovate-updates 2>&1 >build.log
 `
+
init image:quay.io/mytestworkload/test-renovate-updates-utils:0.1@sha256:a3571deec9853dcd91dbc75f9528cfd9439aa9a81b1802e86ad3b8ee783ceeb7


THIS IS FOR CHECKING FROM WHERE RENOVATE FINDS OUT THE EXECUTABLE FOR A POST-UPGRADE TASK.
