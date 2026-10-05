# site/

A single static page plus one generated JSON file. No build step, no Node
toolchain, no framework — the website has the same dependency footprint as the
rest of the repository.

- `index.html` — the page. Fetches `progress.json` at load.
- `progress.json` — **generated**. Do not edit it by hand.

Regenerate locally:

```bash
./scripts/n2t site
```

That runs the whole test suite, probes every chip for whether it is built and
what it costs in NAND gates, and writes the JSON. The page is then viewable by
serving this directory (`python3 -m http.server -d site`) — opening the file
directly with `file://` will not work, because `fetch` needs a real origin.

In CI, `.github/workflows/progress.yml` does the same thing on every push to
`main` and commits the result, which is what triggers the Vercel deployment.
