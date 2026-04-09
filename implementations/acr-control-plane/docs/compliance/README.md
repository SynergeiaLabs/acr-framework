# Compliance Package

This folder is the enterprise review package for the ACR control plane implementation.

It is designed to give security, risk, audit, and platform teams a starting set of artifacts for architecture review, control mapping, and deployment approval.

## Included Artifacts

- [threat-model.md](threat-model.md)
- [shared-responsibility-matrix.md](shared-responsibility-matrix.md)
- [control-mapping.md](control-mapping.md)
- [evidence-package.md](evidence-package.md)
- [external-assessment-scope.md](external-assessment-scope.md)
- [provenance-and-verification.md](../provenance-and-verification.md)
- [failure-load-dr-validation-2026-04-08.md](../failure-load-dr-validation-2026-04-08.md)

## Intended Use

Use this package when:

- a security team is reviewing the control plane before deployment
- a risk or compliance team needs a control narrative
- an enterprise buyer requests architecture, evidence, or shared-responsibility material
- an assessor needs an agreed scope for penetration testing or architecture review

## Important Limits

This package is:

- a technical and operational evidence set
- a reference mapping, not a certification claim
- deployment-aware, not deployment-complete

This package is not:

- legal advice
- a substitute for an organization’s own risk acceptance process
- proof that every deployment of ACR is compliant by default

## Build the Versioned Package

From the implementation root:

```bash
python scripts/build_compliance_package.py \
  --implementation-dir . \
  --version v1.0.1 \
  --source-ref <git-sha> \
  --output-dir dist/compliance
```

That command creates:

- a release tarball
- a manifest with file digests
- a checksum file for the release assets
