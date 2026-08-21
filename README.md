# tayloramurphy.com

Consolidated source for [tayloramurphy.com](https://tayloramurphy.com/).

This repo is the GitLab Pages Jekyll site (`tayloramurphy/tayloramurphy.gitlab.io`) plus the only unique files from the older GitHub Pages repo (`tayloramurphy/tayloramurphy.github.io`). Overlapping posts were not copied twice.

## Remotes

- `origin` — https://github.com/tayloramurphy/tayloramurphy.com.git (this site)
- `gitlab` — https://gitlab.com/tayloramurphy/tayloramurphy.gitlab.io.git (old GitLab Pages host)
- `github` — https://github.com/tayloramurphy/tayloramurphy.github.io.git (2015–2018 Hyde/Poole blog)

## What was merged

GitLab already imported the published GitHub posts on 2020-04-19 (`github posts`). Shared post bodies match except one GitLab typo fix in `2018-03-13-new-job.md` (`THe` → `The`).

Added from GitHub, because they were not on GitLab:

| File | Origin | Notes |
| --- | --- | --- |
| `_posts/2018-05-09-okrs.md` | GitHub branch `personalokrs` (never merged) | Finished post, never published on either live site |
| `_posts/2015-11-18-most-machine-learning-is-search.markdown` | GitHub `master` | Unpublished stub (`published: false`, body is `Stuff`) |

GitHub had 12 posts on `master`; 11 of those were already on GitLab. GitLab has 104 posts total, including the WordPress-era archive (2012–2014) under `_posts/` and images under `wp-content/uploads/`.

`about.md` is leftover Jekyll theme boilerplate, not a real about page.

## Build the new site

Night-telemetry static site. Posts keep their old permalinks.

```sh
uv sync --group dev
uv run pytest
uv run tamweb
uv run python -m http.server --directory public
```

That writes `public/`: homepage, `/writing/`, and one folder per post (`/thoughts-on-identity/`, `/meltano-introduction/`, and so on). WordPress images land at `/wp-content/`. The unpublished stub is skipped.

Background circuits: `uv run python scripts/fetch_tracks.py` rebuilds `source/tracks.json` from the bacinger F1 GeoJSON plus OSM extracts. See `source/tracks-attribution.md`.

## Deploy to Cloudflare

The site deploys as a Worker with static assets. `wrangler.jsonc` points Cloudflare at `public/`. There is no Worker script.

```sh
uv run tamweb
npx wrangler deploy
```

Only `public/` is uploaded. `_posts/`, `source/`, and this README stay in the repo.

In the Cloudflare dashboard, **Workers & Pages** → **Create** → **Import a repository** → `tayloramurphy/tayloramurphy.com`:

| Field | Value |
| --- | --- |
| Build command | `curl -LsSf https://astral.sh/uv/install.sh \| sh && $HOME/.local/bin/uv run tamweb` |
| Deploy command | `npx wrangler deploy` |

Every push to `master` redeploys. Other branches get a preview URL.

### Custom domain

`tayloramurphy.com` is an apex domain. Cloudflare wants apex domains on the same account, so the nameservers have to move off Porkbun onto Cloudflare (same as `starsystems.to`). There are currently no MX records on this domain.

Until that cutover, Porkbun still points the apex at GitLab Pages and the Let’s Encrypt cert there is expired.

GitHub Pages at `tayloramurphy.github.io` is a separate, older build and is not the custom domain.
