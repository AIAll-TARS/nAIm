# Contributing to nAIm

Thanks for helping improve nAIm.

## Ground rules

- Be respectful and precise.
- Keep PRs focused and small.
- Do not commit secrets, tokens, or private infrastructure data.
- For significant changes, open an issue first.

## Development flow

1. Fork and create a feature branch.
2. Set up backend/frontend locally.
3. Make changes with tests or reproducible validation steps.
4. Run checks before opening PR.
5. Submit PR with clear context and impact.

## Local checks

### Backend

```bash
cd backend
python -m pytest
```

### Frontend

```bash
cd frontend
npm run lint
npm run build
```

## Commit style

Use clear, intent-first messages, for example:

- `feat(api): add service filtering by auth_type`
- `fix(frontend): handle missing pricing notes`
- `docs: clarify AGPL/commercial licensing`

## Security requirements

- Never hardcode API keys.
- Use environment variables for all credentials.
- If you find a leak, report it privately to maintainers.

## Licensing and rights

By contributing, you agree your contribution is licensed under AGPL-3.0 for the open-source project.

For future dual-licensing/commercial distribution, maintainers may require a Contributor License Agreement (CLA) in a later phase.

## Pull request checklist

- [ ] No secrets or tokens in code/docs
- [ ] Docs updated if behavior changed
- [ ] OpenAPI updated when API contract changed
- [ ] Lint/build/tests pass
- [ ] PR description explains what and why
