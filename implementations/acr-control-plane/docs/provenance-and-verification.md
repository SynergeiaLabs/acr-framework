# Provenance and Verification

This implementation now includes a release path designed for enterprise verification, not just distribution.

## What Gets Produced

The active release workflow is [`acr-control-plane-release.yml`](../../../.github/workflows/acr-control-plane-release.yml).

For each tagged release it is intended to produce:

- signed container images for:
  - `ghcr.io/<owner>/<repo>/acr-gateway`
  - `ghcr.io/<owner>/<repo>/acr-killswitch`
- GitHub build provenance attestations for those images
- a versioned compliance package tarball
- a Sigstore bundle for the compliance package tarball
- release assets containing the compliance package, manifest, checksums, and signature bundle

## Trust Model

Release verification assumes:

- images are built from the tagged repository state by GitHub Actions
- GitHub OIDC is used for keyless signing
- Sigstore and GitHub artifact attestations are the source of truth for build identity
- deployers verify by digest, not just by tag

## Verify a Container Signature

Use `cosign` against the image digest:

```bash
cosign verify \
  --certificate-identity-regexp "^https://github.com/<owner>/<repo>/.github/workflows/acr-control-plane-release.yml@refs/tags/v.*$" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  ghcr.io/<owner>/<repo>/acr-gateway@sha256:<digest>
```

Repeat for `acr-killswitch` with its own digest.

Why this matters:

- the digest prevents tag-rebinding attacks
- the workflow identity ties the signature to the intended release workflow

## Verify GitHub Build Provenance

Use the GitHub CLI against the image reference:

```bash
docker login ghcr.io
gh attestation verify \
  oci://ghcr.io/<owner>/<repo>/acr-gateway@sha256:<digest> \
  -R <owner>/<repo>
```

Use the same pattern for `acr-killswitch`.

## Verify the Compliance Package Signature

The compliance package is signed as a blob and shipped with a Sigstore bundle:

```bash
cosign verify-blob \
  acr-control-plane-compliance-package-v1.1.0.tar.gz \
  --bundle acr-control-plane-compliance-package-v1.1.0.sigstore.json \
  --certificate-identity-regexp "^https://github.com/<owner>/<repo>/.github/workflows/acr-control-plane-release.yml@refs/tags/v.*$" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com"
```

Then verify the tarball checksum:

```bash
shasum -a 256 -c acr-control-plane-compliance-package-v1.1.0.sha256
```

## Operational Guidance

- Pin deployments by digest, not mutable tags.
- Verify signatures and provenance before promotion into staging or production.
- Store verification output as part of the release approval record.
- Treat signature failure, missing attestations, or digest drift as release blockers.

## Known Scope

This release path proves:

- who built the release artifact
- what workflow identity signed it
- what immutable image or blob digest was produced

It does not by itself prove:

- that the deployment environment is correctly segmented
- that runtime policy was configured safely after install
- that downstream systems are protected from direct access

Those remain part of the deployment and compliance package.
