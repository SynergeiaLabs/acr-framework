# Pre-push checklist (then delete this file)

Use this once before replacing GitHub content, then remove the file.

## Content & links
- [ ] All docs live under `docs/` (pillars, architecture, specs, compliance, security, guides).
- [ ] Root has only: README, LICENSE, CONTRIBUTING, ROADMAP, ADOPTION, GOVERNANCE, SECURITY, CODE_OF_CONDUCT, CHANGELOG, .gitignore.
- [ ] No broken internal links (run link-check if desired: see below).
- [ ] `docs/images/` is empty; add PNGs here when you have them and update architecture image paths if needed.

## Repo settings
- [ ] Default branch is `main` (workflow triggers on `main`). If your repo uses `master`, either rename to `main` in GitHub or change `.github/workflows/link-check.yml` to `branches: [master]`.
- [ ] GitHub Discussions enabled if you want the README/Docs links to work (optional; link-check ignores external URLs).

## How to push (keep repo + history)
To **replace** content but keep the same repo (and issues/stars):

1. In your local repo: `git add -A && git status` (confirm no unintended files).
2. Commit: `git commit -m "Restructure: docs/, ADOPTION, GOVERNANCE, STRIKE expansion, maturity model"`.
3. Push: `git push origin main` (or your branch). Resolve any conflicts with remote.
4. If the remote has a different history and you want this tree to be the new truth: `git push origin main --force` (only if you understand this overwrites remote history).

## How to push (clean slate, new repo)
If you are creating a **new** repo and uploading this folder:

1. Create the new repo on GitHub (empty, no README).
2. Locally: `git init && git add -A && git commit -m "ACR Framework v1.0"`.
3. `git remote add origin <new-repo-url> && git branch -M main && git push -u origin main`.

You will lose issues/stars from the old repo unless you migrate them.

## Optional: run link-check locally
```bash
npx markdown-link-check README.md docs/README.md
# or install markdown-link-check and run on full repo
```

---
Delete this file after you push: `rm PRE-PUSH-CHECKLIST.md && git add -A && git commit -m "Remove pre-push checklist"`
