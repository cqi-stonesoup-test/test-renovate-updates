# test-renovate-updates

Run Renovate:

`LOG_LEVEL=debug RENOVATE_CONFIG_FILE="$RENOVATE_GLOBAL_CONFIG" renovate --token "$GH_TOKEN" cqi-stonesoup-test/test-renovate-updates 2>&1 >build.log
`
Doing migration:
from: quay.io/mytestworkload/test-renovate-updates-utils:0.1@sha256:379731c4d9c34df58fc330916aeba631826735b3c371dbf63c57b59bb28eae44
to: quay.io/mytestworkload/test-renovate-updates-utils:0.1@sha256:3570ac367c2b47a38dc82b7fecb2bb814a057249e7de485478722b4dd8b0b15b
inspect image: quay.io/mytestworkload/test-renovate-updates-utils:0.1@sha256:3570ac367c2b47a38dc82b7fecb2bb814a057249e7de485478722b4dd8b0b15b
{
  "digest": "sha256:3570ac367c2b47a38dc82b7fecb2bb814a057249e7de485478722b4dd8b0b15b",
  "is_manifest_list": false,
  "manifest_data": "{\"schemaVersion\":2,\"mediaType\":\"application/vnd.oci.image.manifest.v1+json\",\"config\":{\"mediaType\":\"application/vnd.oci.image.config.v1+json\",\"digest\":\"sha256:71998035a45ae5a9f0ffb753c9105f72839d9945943174870bb474a52c092b08\",\"size\":2755},\"layers\":[{\"mediaType\":\"application/vnd.oci.image.layer.v1.tar+gzip\",\"digest\":\"sha256:498ce84ac34c70f2bce9630eec216a33f8ab0f345702a830826548f773e351ec\",\"size\":48775561},{\"mediaType\":\"application/vnd.oci.image.layer.v1.tar+gzip\",\"digest\":\"sha256:d85e25607211b948e45cc3454af809da924753b8b7b3736c86bcc80c5a13fe00\",\"size\":111063}],\"annotations\":{\"org.opencontainers.image.base.digest\":\"sha256:85702231d7fc2d4788888dd5035d42563089fe2590f0d90542582e9a758f7306\",\"org.opencontainers.image.base.name\":\"registry.fedoraproject.org/fedora-minimal:40\"}}",
  "config_media_type": "application/vnd.oci.image.config.v1+json",
  "layers_compressed_size": 48886624,
  "layers": [
    {
      "index": 0,
      "compressed_size": 48775561,
      "is_remote": false,
      "urls": null,
      "command": [
        "KIWI 10.0.21"
      ],
      "comment": null,
      "author": "Fedora Project Contributors <devel@lists.fedoraproject.org>",
      "blob_digest": "sha256:498ce84ac34c70f2bce9630eec216a33f8ab0f345702a830826548f773e351ec",
      "created_datetime": "Thu, 11 Jul 2024 05:49:04 -0000"
    },
    {
      "index": 1,
      "compressed_size": 32,
      "is_remote": false,
      "urls": null,
      "command": [
        "/bin/sh -c #(nop) ARG yq_version"
      ],
      "comment": "FROM registry.fedoraproject.org/fedora-minimal:40",
      "author": "Fedora Project Contributors <devel@lists.fedoraproject.org>",
      "blob_digest": "sha256:a3ed95caeb02ffe68cdd9fd84406680ae93d633cb16422d00e8a7c22955b46d4",
      "created_datetime": "Thu, 22 Aug 2024 06:17:30 -0000"
    },
    {
      "index": 2,
      "compressed_size": 32,
      "is_remote": false,
      "urls": null,
      "command": [
        "/bin/sh -c #(nop) ARG version yq_version"
      ],
      "comment": "FROM e3bb438de672",
      "author": "Fedora Project Contributors <devel@lists.fedoraproject.org>",
      "blob_digest": "sha256:a3ed95caeb02ffe68cdd9fd84406680ae93d633cb16422d00e8a7c22955b46d4",
      "created_datetime": "Thu, 22 Aug 2024 06:17:30 -0000"
    },
    {
      "index": 3,
      "compressed_size": 32,
      "is_remote": false,
      "urls": null,
      "command": [
        "/bin/sh -c #(nop) LABEL     org.opencontainers.image.title=\"utils image for testing renovate update PRs\"     org.opencontainers.image.version=\"${version}\"     org.opencontainers.image.licenses=\"MIT\""
      ],
      "comment": "FROM 8495843c221e",
      "author": "Fedora Project Contributors <devel@lists.fedoraproject.org>",
      "blob_digest": "sha256:a3ed95caeb02ffe68cdd9fd84406680ae93d633cb16422d00e8a7c22955b46d4",
      "created_datetime": "Thu, 22 Aug 2024 06:17:30 -0000"
    },
    {
      "index": 4,
      "compressed_size": 32,
      "is_remote": false,
      "urls": null,
      "command": [
        "/bin/sh -c #(nop) WORKDIR /src"
      ],
      "comment": "FROM cd5afb87e58d",
      "author": "Fedora Project Contributors <devel@lists.fedoraproject.org>",
      "blob_digest": "sha256:a3ed95caeb02ffe68cdd9fd84406680ae93d633cb16422d00e8a7c22955b46d4",
      "created_datetime": "Thu, 22 Aug 2024 06:17:30 -0000"
    },
    {
      "index": 5,
      "compressed_size": 111063,
      "is_remote": false,
      "urls": null,
      "command": [
        "/bin/sh -c #(nop) COPY dir:d48fe8bdac1f203127d617678cbaf49da070a381539db7fbff99dfd2d4b189c4 in . "
      ],
      "comment": "FROM dee6efde7e26",
      "author": "Fedora Project Contributors <devel@lists.fedoraproject.org>",
      "blob_digest": "sha256:d85e25607211b948e45cc3454af809da924753b8b7b3736c86bcc80c5a13fe00",
      "created_datetime": "Mon, 26 Aug 2024 08:23:38 -0000"
    },
    {
      "index": 6,
      "compressed_size": 32,
      "is_remote": false,
      "urls": null,
      "command": [
        "/bin/sh -c #(nop) CMD [\"bash\", \"main.sh\"]"
      ],
      "comment": "FROM 17a946b0aade",
      "author": "Fedora Project Contributors <devel@lists.fedoraproject.org>",
      "blob_digest": "sha256:a3ed95caeb02ffe68cdd9fd84406680ae93d633cb16422d00e8a7c22955b46d4",
      "created_datetime": "Mon, 26 Aug 2024 08:23:38 -0000"
    }
  ]
}
found pipeline bundle: quay.io/konflux-ci/tekton-catalog/pipeline-docker-build:2081db76e67618c5154d230e9a0b115812a6327d
