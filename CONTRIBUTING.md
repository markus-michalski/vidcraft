# Contributing to VidCraft

## Development Setup

```bash
git clone https://github.com/markus-michalski/vidcraft.git
cd vidcraft

# Install as Claude Code plugin
claude plugin install ./vidcraft

# Run first-time setup (in Claude Code)
/vidcraft:setup
```

## Architecture

VidCraft is a Claude Code plugin with an MCP server and specialized skills:

```
skills/              # Claude Code skills (one .md per skill)
mcp-server/          # Python MCP server
  src/               # Server source code
video-types/         # Video type definitions
config/              # Configuration templates
```

### Adding a New Skill

1. Create `skills/your-skill/SKILL.md` with frontmatter (name, description, argument-hint, user-invocable)
2. Skills must be flat — no subdirectories inside a skill folder
3. Add a routing entry in `CLAUDE.md`

### Adding a New Video Type

Use `/vidcraft:video-type-creator` or manually create `video-types/<type>/README.md` following the existing type structure.

## Code Style

- **Python:** PEP 8, type hints, English comments
- **Markdown:** YAML frontmatter always present in project/episode/scene files
- **Skills:** Flat structure, only `name`/`description`/`argument-hint`/`user-invocable` as frontmatter

## Testing

```bash
cd mcp-server
pip install -r requirements.txt
# Run MCP server locally for testing
python -m src.server
```

## Commits

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new skill or video type
fix: correct a bug
docs: update documentation
refactor: restructure code
```

## Pull Requests

1. Create a feature branch from `main`
2. Make your changes
3. Ensure the MCP server starts without errors
4. Open a PR with a clear description
