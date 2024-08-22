# test-renovate-updates

Run Renovate:

`LOG_LEVEL=debug RENOVATE_CONFIG_FILE="$RENOVATE_GLOBAL_CONFIG" renovate --token "$GH_TOKEN" cqi-stonesoup-test/test-renovate-updates 2>&1 >build.log
`


Doing migration:
from: quay.io/mytestworkload/test-renovate-updates-utils:0.1@sha256:54a83e8827a50f33256bce35f8ddf86dfe8e21c9125fa013f4f9009fddda9d8e
to:   quay.io/mytestworkload/test-renovate-updates-utils:0.1@sha256:c07b6a0bfd44d0cd1d8adb0e34153c1ddd811b87d1d9446c59a4c402c931b797


diff --git a/pipelinerun.yaml b/pipelinerun.yaml
index 61a6f3c..c0d637b 100644
--- a/pipelinerun.yaml
+++ b/pipelinerun.yaml
@@ -15,7 +15,7 @@ spec:
           - name: name
             value: init
           - name: bundle
-            value: quay.io/mytestworkload/test-renovate-updates-utils:0.1@sha256:54a83e8827a50f33256bce35f8ddf86dfe8e21c9125fa013f4f9009fddda9d8e
+            value: quay.io/mytestworkload/test-renovate-updates-utils:0.1@sha256:c07b6a0bfd44d0cd1d8adb0e34153c1ddd811b87d1d9446c59a4c402c931b797
           - name: kind
             value: task
         resolver: bundles

run: skopeo inspect docker://quay.io/mytestworkload/test-renovate-updates-utils@sha256:c07b6a0bfd44d0cd1d8adb0e34153c1ddd811b87d1d9446c59a4c402c931b797
{
    "Name": "quay.io/mytestworkload/test-renovate-updates-utils",
    "Digest": "sha256:c07b6a0bfd44d0cd1d8adb0e34153c1ddd811b87d1d9446c59a4c402c931b797",
    "RepoTags": [
        "0.1",
        "0.1-14271c33194e43435c087d6f7dfd20665321fc5d",
        "0.1-1875b3ea7ebc556ef086b85638675e56735a6a9a",
        "0.1-1c0d0c3ab8045ad1a2a349ac0084be8933fd2067",
        "0.1-20435aa55007dac1075a0de0bebcd89a8267c5f4",
        "0.1-20a7298b8c4c8235d4a7af39f2ca5abc84d1fb2c",
        "0.1-2651d47575a1def24b1ad20b5a4769960550635b",
        "0.1-26708a17f07dc68a98cc0417466cd302cf702e6b",
        "0.1-42b50e3373700afee6bd1c1cf69c0f5b01d9dce7",
        "0.1-4459f3532bf6930fef4f8602dc185b522ab28995",
        "0.1-470149e4c9c00a9bae0c773b1625857d07ef1021",
        "0.1-5996568165a748a09afac2583e0f57dd4222e804",
        "0.1-5e1d66039d51709198e2478abe58b69b68bd0332",
        "0.1-67cc4c80ab4b6982f55336f747865bee9df19cb2",
        "0.1-68e3a8ab4b17e8379e35238fa4bc3c253edc0423",
        "0.1-7f7741b74cddd2d90d93d57ea0ae4c2973308a80",
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
    "Created": "2024-08-22T07:29:36.907468017Z",
    "DockerVersion": "",
    "Labels": {
        "io.buildah.version": "1.37.1",
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
        "sha256:828f60c1d602b277562645688d7140fedc87ace742299ce72548635d3d906530"
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
            "Digest": "sha256:828f60c1d602b277562645688d7140fedc87ace742299ce72548635d3d906530",
            "Size": 64746,
            "Annotations": null
        }
    ],
    "Env": [
        "container=oci",
        "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
    ]
}
