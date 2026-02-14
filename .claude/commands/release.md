# Release Procedure

Skills marketplace release. Version tracked per skill.

---

[!IMPORTANT]: **BEFORE ANY RELEASE, CREATE A CHECKLIST WITH TodoWrite.**

Do NOT release from memory. Create tasks for each step and mark them complete as you go.

**Release Checklist (copy to TodoWrite):**

```
1. All changes committed with conventional prefixes (see Commit Conventions)
2. Version bumped in ALL version files that exist for this skill (see Version Files)
3. If skill has a build system, build and test pass
4. git push origin main
```

---

[!VERSION-FILES]: Two version files are guaranteed across all skills. Additional version files may exist depending on the skill's internal structure (e.g. package.json, Cargo.toml, setup.py). All that exist MUST match.

```yaml
version_files:
  # Always present:
  - file: SKILL.md
    path: plugins/<skill>/SKILL.md
    field: frontmatter → version
    read_by: Agent (skill loader)
  - file: marketplace.json
    path: .claude-plugin/marketplace.json
    field: plugins[name=<skill>].version
    read_by: Marketplace registry
  # Skill-specific (check if they exist):
  # Any file that declares a version (package.json, Cargo.toml, pyproject.toml, etc.)
  # must be kept in sync with the above two.
```

[!VERSION-SYNC-RULE]: **If any version files diverge, align them all before releasing.**

---

[!VERSION-BUMP]: Before each release, REASON about what bump is appropriate:

- Run `git log <last-tag>..HEAD --oneline` to see all changes since last release
- Apply the commit convention rules to determine the bump
- Semver: patch (0.0.X), minor (0.X.0), major (X.0.0)

---

[!COMMIT-CONVENTIONS]: Use conventional prefixes scoped to the skill:

```yaml
prefixes:
  - prefix: "fix(<skill>):"
    meaning: Bug fix
    bump: patch
  - prefix: "feat(<skill>):"
    meaning: New feature
    bump: minor
  - prefix: "breaking(<skill>):"
    meaning: Breaking change
    bump: major
  - prefix: "refactor(<skill>):"
    meaning: Code restructuring, no behavior change
    bump: patch
  - prefix: "docs(<skill>):"
    meaning: Documentation only
    bump: patch
  - prefix: "chore(<skill>):"
    meaning: Build, tooling, maintenance
    bump: patch
```

Commit message format: `<prefix>(<skill>): <description>, bump to <version>`

The highest-priority prefix in the log determines the bump:
- Any `breaking:` in the log -> major
- Any `feat:` -> minor
- Only `fix:`/`refactor:`/`docs:`/`chore:` -> patch

---

[!RELEASE-PROCEDURE]: To release a new version of a skill:

1. **Make changes** in `plugins/<skill>/`

2. **Bump version** in all version files that exist for this skill (see Version Files)

3. **If the skill has a build system** (package.json, Makefile, Cargo.toml, setup.py, etc.), run the build and tests.

4. **Stage files**
   ```bash
   git add .claude-plugin/marketplace.json plugins/<skill>/...
   ```
   If the skill produces build artifacts that are gitignored, use `git add -f` to include them.

5. **Commit** with conventional prefix
   ```bash
   git commit -m "<prefix>(<skill>): <description>, bump to X.Y.Z"
   ```

6. **Push**
   ```bash
   git push origin main
   ```
