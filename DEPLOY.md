# Publishing the progress site

The site is a single static page (`site/index.html`) plus one generated file
(`site/progress.json`). No build step, no Node toolchain — the website has the
same dependency footprint as the rest of the repository.

## One-time setup

**1. Push the repository to GitHub.**

```bash
git add -A && git commit -m "nand2tetris: projects 1-2 and the progress site"
gh repo create nand2tetris --public --source=. --remote=origin --push
```

(Or create the repo in the GitHub UI and `git remote add origin … && git push -u origin main`.)

**2. Connect it to Vercel.**

At <https://vercel.com/new>, import the repository. `vercel.json` already tells
Vercel everything it needs:

| Setting | Value | Why |
| --- | --- | --- |
| Framework preset | Other | there is nothing to build |
| Build command | *(leave empty)* | the JSON is generated in CI, not at deploy time |
| Output directory | `site` | set by `vercel.json` |

Deploy. That is the whole setup.

> **Why there is no `pyproject.toml` in this repository.** Vercel inspects the
> repository root to decide what kind of project it is. A `pyproject.toml` there
> makes it classify the repo as a Python web app, ignore `outputDirectory`, and
> fail with *"No python entrypoint found."* The pytest configuration therefore
> lives in `pytest.ini`, which Vercel does not react to. Nothing is installed as
> a package here, so `pyproject.toml` was buying us nothing anyway.
>
> If a future change reintroduces that failure, the guaranteed fix is a project
> setting rather than a file: in Vercel, **Settings → Build and Deployment →
> Root Directory**, set it to `site`. Vercel then only ever looks inside `site/`,
> which contains nothing but HTML and JSON. Move `vercel.json` into `site/` and
> drop its `outputDirectory` line if you go that route.

**3. Fix the GitHub link in the page footer.**

`site/index.html` links to `github.com/epillon/nand2tetris`. Change it if your
repository lives somewhere else.

## How it stays up to date

```
you solve a chip  →  git push  →  GitHub Action runs the suite
                                  →  writes site/progress.json
                                  →  commits it
                                  →  Vercel deploys
```

`.github/workflows/progress.yml` installs pytest, runs
`python tools/emit_progress.py`, and commits the result only if it changed.
Pushes made with `GITHUB_TOKEN` do not retrigger workflows, so this cannot loop.

Nothing on the page is typed in by hand. Every number — tests passing, chips
built, NAND cost against par — comes from running the suite and probing your
chips. If you fake a chip, the site says so.

## Locally

```bash
./scripts/n2t site                     # re-measure
python3 -m http.server -d site 8787    # then open http://localhost:8787
```

Opening `index.html` as a `file://` URL will not work — `fetch` needs a real
origin.

## Adding a side quest

Edit `SIDE_QUESTS` in `tools/registry.py` and run `./scripts/n2t site`. Each
entry says which project unlocks it, roughly what it costs you, and what kind of
thing it is. Set `status="started"` or `status="done"` as you go.
