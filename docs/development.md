# Development

## Setup

```bash
pip install -e ".[dev,docs]"
cp .env.example .env
tl-guard doctor
pytest -q
```

## Docs site (MkDocs Material)

```bash
# live reload while editing docs/
mkdocs serve -a 127.0.0.1:8001

# static site → site/
mkdocs build --clean
```

Serve the built static site (e.g. after CI):

```bash
python -m http.server 8001 --directory site
```

### GitHub Pages (optional host)

```bash
mkdocs gh-deploy
```

Or push the `site/` folder via your CI Pages workflow.

## Tests

- Production code: **Ollama / OpenAI only**.  
- Unit tests: inject `FakeLLM` into `TLGuardAgent(llm=...)`.  
- Do not reintroduce a production MockLLM.

```bash
pytest -q
python experiments/e1_lsm_validation.py
```

## Project plan

See root `plan.md` for the research/engineering roadmap. MkDocs covers the **product workflow**; the plan covers multi-week evaluation phases.
