# test-renovate-updates

Run Renovate:

`LOG_LEVEL=debug RENOVATE_CONFIG_FILE="$RENOVATE_GLOBAL_CONFIG" renovate --token "$GH_TOKEN" cqi-stonesoup-test/test-renovate-updates 2>&1 >build.log
`

diff --git a/README.md b/README.md
index dc3f096..e61d4b9 100644
--- a/README.md
+++ b/README.md
@@ -4,3 +4,4 @@ Run Renovate:
 
 `LOG_LEVEL=debug RENOVATE_CONFIG_FILE="$RENOVATE_GLOBAL_CONFIG" renovate --token "$GH_TOKEN" cqi-stonesoup-test/test-renovate-updates 2>&1 >build.log
 `
+
diff --git a/pipelinerun.yaml b/pipelinerun.yaml
index 9d272e3..5b10ded 100644
--- a/pipelinerun.yaml
+++ b/pipelinerun.yaml
@@ -15,7 +15,7 @@ spec:
       - name: name
         value: init
       - name: bundle
-        value: quay.io/mytestworkload/test-renovate-updates-utils:0.1@sha256:a3571deec9853dcd91dbc75f9528cfd9439aa9a81b1802e86ad3b8ee783ceeb7
+        value: quay.io/mytestworkload/test-renovate-updates-utils:0.1@sha256:d9523a9863cb222674855f8fa05bb376a2c1a802d29a9df316806b9dd8c7009b
       - name: kind
         value: task
       resolver: bundles


init image:quay.io/mytestworkload/test-renovate-updates-utils:0.1@sha256:d9523a9863cb222674855f8fa05bb376a2c1a802d29a9df316806b9dd8c7009b


THIS IS FOR CHECKING FROM WHERE RENOVATE FINDS OUT THE EXECUTABLE FOR A POST-UPGRADE TASK.
run: skopeo inspect docker://quay.io/mytestworkload/test-renovate-updates-utils@sha256:d9523a9863cb222674855f8fa05bb376a2c1a802d29a9df316806b9dd8c7009b
{
    "Name": "quay.io/mytestworkload/test-renovate-updates-utils",
    "Digest": "sha256:d9523a9863cb222674855f8fa05bb376a2c1a802d29a9df316806b9dd8c7009b",
    "RepoTags": [
        "0.1",
        "0.1-1875b3ea7ebc556ef086b85638675e56735a6a9a",
        "0.1-1c0d0c3ab8045ad1a2a349ac0084be8933fd2067",
        "0.1-20435aa55007dac1075a0de0bebcd89a8267c5f4",
        "0.1-20a7298b8c4c8235d4a7af39f2ca5abc84d1fb2c",
        "0.1-2651d47575a1def24b1ad20b5a4769960550635b",
        "0.1-26708a17f07dc68a98cc0417466cd302cf702e6b",
        "0.1-470149e4c9c00a9bae0c773b1625857d07ef1021",
        "0.1-5996568165a748a09afac2583e0f57dd4222e804",
        "0.1-5e1d66039d51709198e2478abe58b69b68bd0332",
        "0.1-67cc4c80ab4b6982f55336f747865bee9df19cb2",
        "0.1-8e413855b0a4f97057e8a5892d3cc547d0c94910",
        "0.1-a0e51b89f72b43518852826f400ebdd55018e44a",
        "0.1-a3c88c85651e3e360f640715831b95377d6781bb",
        "0.1-a8dfd258f6b040ca9777d071cb7ae16b907f8533",
        "0.1-a8fa00f9c123bd96006eb1c823a0583043a0f9e6",
        "0.1-b5dbb0c59f4e41741a94d1d67ff6ef7d2fc14f9a",
        "0.1-dacea717abe6aef46adb36281f37ac1e379cef16",
        "2024-08-21T1608560800"
    ],
    "Created": "2024-08-21T14:08:15.219853078Z",
    "DockerVersion": "",
    "Labels": {
        "io.buildah.version": "1.37.0",
        "license": "MIT",
        "name": "fedora-minimal",
        "org.opencontainers.image.license": "MIT",
        "org.opencontainers.image.licenses": "MIT",
        "org.opencontainers.image.name": "fedora-minimal",
        "org.opencontainers.image.title": "utils image for testing renovate update PRs",
        "org.opencontainers.image.url": "https://fedoraproject.org/",
        "org.opencontainers.image.vendor": "Fedora Project",
        "org.opencontainers.image.version": "0.1",
        "vendor": "Fedora Project",
        "version": "40"
    },
    "Architecture": "amd64",
    "Os": "linux",
    "Layers": [
        "sha256:498ce84ac34c70f2bce9630eec216a33f8ab0f345702a830826548f773e351ec",
        "sha256:1cca9fc155dc9b1ef7f66a82752a476e8edd985e7f64f42122b338060ac33944"
    ],
    "LayersData": [
        {
            "MIMEType": "application/vnd.oci.image.layer.v1.tar+gzip",
            "Digest": "sha256:498ce84ac34c70f2bce9630eec216a33f8ab0f345702a830826548f773e351ec",
            "Size": 48775561,
            "Annotations": null
        },
        {
            "MIMEType": "application/vnd.oci.image.layer.v1.tar+gzip",
            "Digest": "sha256:1cca9fc155dc9b1ef7f66a82752a476e8edd985e7f64f42122b338060ac33944",
            "Size": 49244,
            "Annotations": null
        }
    ],
    "Env": [
        "container=oci",
        "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
    ]
}
