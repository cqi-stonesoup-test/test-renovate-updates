# test-renovate-updates

Run Renovate:

`LOG_LEVEL=debug RENOVATE_CONFIG_FILE="$RENOVATE_GLOBAL_CONFIG" renovate --token "$GH_TOKEN" cqi-stonesoup-test/test-renovate-updates 2>&1 >build.log
`

dep: @sha256:66a7a2f6d5fe5c6980c6c70dc86c45373c3f0d755816940412ad9b470d9d58c7
diff --git a/pipelinerun.yaml b/pipelinerun.yaml
index 7fc9c1f..42ff6cf 100644
--- a/pipelinerun.yaml
+++ b/pipelinerun.yaml
@@ -25,7 +25,7 @@ spec:
           - name: name
             value: summary
           - name: bundle
-            value: quay.io/konflux-ci/tekton-catalog/task-summary:0.1@sha256:594a6dc7e331e7e5f2500940fb7197afb479d7f6d1650213d1bd58ce874e1500
+            value: quay.io/konflux-ci/tekton-catalog/task-summary:0.1@sha256:66a7a2f6d5fe5c6980c6c70dc86c45373c3f0d755816940412ad9b470d9d58c7
           - name: kind
             value: task
         resolver: bundles

run: skopeo inspect docker://quay.io/mytestworkload/test-renovate-updates-utils@sha256:ae61990695eb4cbc926a2d442944f92f9eb37c17ae16c72211da69526d428036
{
    "Name": "quay.io/mytestworkload/test-renovate-updates-utils",
    "Digest": "sha256:ae61990695eb4cbc926a2d442944f92f9eb37c17ae16c72211da69526d428036",
    "RepoTags": [
        "0.1",
        "0.1-1875b3ea7ebc556ef086b85638675e56735a6a9a",
        "0.1-1c0d0c3ab8045ad1a2a349ac0084be8933fd2067",
        "0.1-20435aa55007dac1075a0de0bebcd89a8267c5f4",
        "0.1-20a7298b8c4c8235d4a7af39f2ca5abc84d1fb2c",
        "0.1-2651d47575a1def24b1ad20b5a4769960550635b",
        "0.1-26708a17f07dc68a98cc0417466cd302cf702e6b",
        "0.1-42b50e3373700afee6bd1c1cf69c0f5b01d9dce7",
        "0.1-470149e4c9c00a9bae0c773b1625857d07ef1021",
        "0.1-5996568165a748a09afac2583e0f57dd4222e804",
        "0.1-5e1d66039d51709198e2478abe58b69b68bd0332",
        "0.1-67cc4c80ab4b6982f55336f747865bee9df19cb2",
        "0.1-68e3a8ab4b17e8379e35238fa4bc3c253edc0423",
        "0.1-8e413855b0a4f97057e8a5892d3cc547d0c94910",
        "0.1-a0e51b89f72b43518852826f400ebdd55018e44a",
        "0.1-a3c88c85651e3e360f640715831b95377d6781bb",
        "0.1-a8dfd258f6b040ca9777d071cb7ae16b907f8533",
        "0.1-a8fa00f9c123bd96006eb1c823a0583043a0f9e6",
        "0.1-b5dbb0c59f4e41741a94d1d67ff6ef7d2fc14f9a",
        "0.1-d5516516ac61282c74ee5b4a2e8ce82578dfd95e",
        "0.1-dacea717abe6aef46adb36281f37ac1e379cef16",
        "0.1-ef6fd206fa40940015e5b77e04234ffefdbe475d",
        "2024-08-21T1608560800"
    ],
    "Created": "2024-08-21T09:56:42.689945823Z",
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
        "sha256:47af7a559706c2a0ac58ae3c001b1e48d64b8f9dff5e94acc2cf794daaf6bdad"
    ],
    "LayersData": [
        {
            "MIMEType": "application/vnd.oci.image.layer.v1.tar+gzip",
            "Digest": "sha256:47af7a559706c2a0ac58ae3c001b1e48d64b8f9dff5e94acc2cf794daaf6bdad",
            "Size": 48835826,
            "Annotations": null
        }
    ],
    "Env": [
        "container=oci",
        "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
    ]
}
