# Publishing the HACS Integration from the Main Repository

This guide explains how to publish the `homeassistant/` subdirectory of the
[AvalonMiner](https://github.com/mkeller0815/AvalonMiner) monorepo as a
standalone HACS-compatible repository at
**<https://github.com/mkeller0815/HACS-Avalon-Miner>**.

The technique used is **git subtree split** -- it extracts only the
`homeassistant/` folder (with full commit history) and pushes it as the root of
the HACS release repo.

## Repository layout

```
AvalonMiner/                          (monorepo)
├── homeassistant/
│   ├── custom_components/
│   │   └── avalon_miner/             (the actual integration)
│   ├── hacs.json
│   └── README.md
└── ...
```

After the subtree push the HACS repo will contain:

```
HACS-Avalon-Miner/                    (release repo)
├── custom_components/
│   └── avalon_miner/
├── hacs.json
└── README.md
```

This is exactly the structure HACS expects.

---

## Initial setup (one-time)

### 1. Create the release repository on GitHub

Create **<https://github.com/mkeller0815/HACS-Avalon-Miner>** as a completely
empty repository -- no README, no license, no `.gitignore`.

### 2. Add a named remote (optional but recommended)

```bash
cd /path/to/AvalonMiner
git remote add hacs-release https://github.com/mkeller0815/HACS-Avalon-Miner.git
```

### 3. Split and push

```bash
git subtree split --prefix=homeassistant -b hacs-release-branch
git push hacs-release hacs-release-branch:main --force
```

### 4. Clean up the local branch

```bash
git branch -D hacs-release-branch
```

---

## Publishing updates

Whenever you have committed changes to the `homeassistant/` directory, run:

```bash
cd /path/to/AvalonMiner

# Make sure everything is committed
git status

# Split and push
git subtree split --prefix=homeassistant -b hacs-release-branch
git push hacs-release hacs-release-branch:main --force

# Clean up
git branch -D hacs-release-branch
```

That's it -- three commands to publish an update.

---

## Creating a release with a version tag

HACS uses GitHub releases / tags as version identifiers. After pushing an
update:

```bash
# Tag in the monorepo (optional, for your own tracking)
git tag v1.0.0
git push origin v1.0.0

# Tag in the HACS release repo
git push hacs-release hacs-release-branch:main --force   # if not already done
git push hacs-release v1.0.0
```

Then go to **<https://github.com/mkeller0815/HACS-Avalon-Miner/releases>** and
create a GitHub release from the tag.

> **Note:** The version tag must match the `version` field in
> `custom_components/avalon_miner/manifest.json`.

---

## Quick-reference cheat sheet

| Task | Command |
|------|---------|
| Add remote (once) | `git remote add hacs-release https://github.com/mkeller0815/HACS-Avalon-Miner.git` |
| Split subtree | `git subtree split --prefix=homeassistant -b hacs-release-branch` |
| Push to HACS repo | `git push hacs-release hacs-release-branch:main --force` |
| Delete local branch | `git branch -D hacs-release-branch` |
| Push version tag | `git push hacs-release v1.0.0` |

---

## Common mistakes

| Problem | Cause |
|---------|-------|
| Merge conflict on push | The HACS repo was not empty on creation (had a README or license) |
| Wrong files in HACS repo | Incorrect `--prefix` value (must be `homeassistant`, not `homeassistant/custom_components`) |
| Push fails | Uncommitted changes in the monorepo -- commit or stash first |
| HACS can't find integration | Missing `hacs.json` or `custom_components/` in the release repo root |

---

## HACS validation checklist

Before publishing, verify that the release repo root contains:

- [ ] `custom_components/avalon_miner/manifest.json` with all required keys
- [ ] `custom_components/avalon_miner/__init__.py`
- [ ] `custom_components/avalon_miner/config_flow.py`
- [ ] `hacs.json` with at least a `name` key
- [ ] `README.md`
