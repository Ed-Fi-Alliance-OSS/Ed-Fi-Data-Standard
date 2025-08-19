---
applyTo: ".github/workflows/**/*"
---

# GitHub Actions Instructions

- Name workflow files and jobs descriptively and consistently
- Use environment variables for sensitive information (e.g., API keys, secrets)
- Reference actions by their full SHA256 commit hash:
   - BAD example: `actions/github-script@latest`
   - BAD example: `actions/github-script@v7.0.1`
   - GOOD example: `actions/github-script@60a0d83039c74a4aee543508d2ffcb1c3799cdea`
- Prefer official actions and marketplace actions with high usage and recent updates
- Add comments to explain non-obvious steps or logic.
- Use `if:` conditions to control step/job execution when needed.
- Always validate YAML syntax before committing.
- Use caching for dependencies to speed up workflows.