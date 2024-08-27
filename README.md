# test-renovate-updates

Run Renovate:

`LOG_LEVEL=debug RENOVATE_CONFIG_FILE="$RENOVATE_GLOBAL_CONFIG" renovate --token "$GH_TOKEN" cqi-stonesoup-test/test-renovate-updates 2>&1 >build.log
`
Doing migration:
from: quay.io/mytestworkload/test-renovate-updates-task-init:0.1@sha256:1007b848c552ae81dc57d230d2d24e987c425a3033f8a268b73422a8ee4b1613
to: quay.io/mytestworkload/test-renovate-updates-task-init:0.1@sha256:ba848bc7c100790658559692b3b05ba1141f143d9dd437df38579019477a5b88
inspect image: quay.io/mytestworkload/test-renovate-updates-task-init:0.1@sha256:ba848bc7c100790658559692b3b05ba1141f143d9dd437df38579019477a5b88
{
  "digest": "sha256:ba848bc7c100790658559692b3b05ba1141f143d9dd437df38579019477a5b88",
  "is_manifest_list": false,
  "manifest_data": "{\"schemaVersion\":2,\"mediaType\":\"application/vnd.docker.distribution.manifest.v2+json\",\"config\":{\"mediaType\":\"application/vnd.docker.container.image.v1+json\",\"size\":238,\"digest\":\"sha256:c2f73ad5c64fa3cf4a4015ecb124c25670e9d83100961ca719c6cfd7a61fdda1\"},\"layers\":[{\"mediaType\":\"application/vnd.docker.image.rootfs.diff.tar.gzip\",\"size\":314,\"digest\":\"sha256:06a94066ed3f96a96ea28cb07c417f6995f005ea3237adda9056ef725f37e06a\",\"annotations\":{\"dev.tekton.image.apiVersion\":\"v1\",\"dev.tekton.image.kind\":\"task\",\"dev.tekton.image.name\":\"init\"}}]}",
  "config_media_type": "application/vnd.docker.container.image.v1+json",
  "layers_compressed_size": 314,
  "layers": [
    {
      "index": 0,
      "compressed_size": 314,
      "is_remote": false,
      "urls": null,
      "command": null,
      "comment": null,
      "author": null,
      "blob_digest": "sha256:06a94066ed3f96a96ea28cb07c417f6995f005ea3237adda9056ef725f37e06a",
      "created_datetime": "Mon, 01 Jan 0001 00:00:00 -0000"
    }
  ]
}
found pipeline bundle: quay.io/mytestworkload/test-renovate-updates-pipeline:c979f58570de40e4ca5e77fc7b7fc7dac9c9fdff
found pipeline bundle: quay.io/mytestworkload/test-renovate-updates-pipeline:18a61693389c6c912df587f31bc3b4cc53eb0d5b
changes to pipeline:

spec.tasks
  + one list entry added:
    - name: buildimage
      runAfter:
      - test
      taskRef:
        params:
        - name: name
          value: buildimage
        - name: bundle
          value: "quay.io/mytestworkload/test-renovate-updates-task-buildimage:0.1@sha256:d30a978b4c90f526c1884c2351f15f385e8609247de2900608418498b53604d4"
        - name: kind
          value: task
        resolver: bundles
    
  

spec.tasks.init.taskRef.params.bundle.value
  ± value change
    - quay.io/mytestworkload/test-renovate-updates-task-init:0.1@sha256:1007b848c552ae81dc57d230d2d24e987c425a3033f8a268b73422a8ee4b1613
    + quay.io/mytestworkload/test-renovate-updates-task-init:0.1@sha256:ba848bc7c100790658559692b3b05ba1141f143d9dd437df38579019477a5b88
  


