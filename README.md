# tayloramurphy.com

Consolidated source for [tayloramurphy.com](https://tayloramurphy.com/).

This repo is the GitLab Pages Jekyll site (`tayloramurphy/tayloramurphy.gitlab.io`) plus the only unique files from the older GitHub Pages repo (`tayloramurphy/tayloramurphy.github.io`). Overlapping posts were not copied twice.

## Remotes

- `gitlab` — https://gitlab.com/tayloramurphy/tayloramurphy.gitlab.io.git (what currently serves the domain)
- `github` — https://github.com/tayloramurphy/tayloramurphy.github.io.git (2015–2018 Hyde/Poole blog)

Nothing has been pushed back to either host yet.

## What was merged

GitLab already imported the published GitHub posts on 2020-04-19 (`github posts`). Shared post bodies match except one GitLab typo fix in `2018-03-13-new-job.md` (`THe` → `The`).

Added from GitHub, because they were not on GitLab:

| File | Origin | Notes |
| --- | --- | --- |
| `_posts/2018-05-09-okrs.md` | GitHub branch `personalokrs` (never merged) | Finished post, never published on either live site |
| `_posts/2015-11-18-most-machine-learning-is-search.markdown` | GitHub `master` | Unpublished stub (`published: false`, body is `Stuff`) |

GitHub had 12 posts on `master`; 11 of those were already on GitLab. GitLab has 104 posts total, including the WordPress-era archive (2012–2014) under `_posts/` and images under `wp-content/uploads/`.

`about.md` is leftover Jekyll theme boilerplate, not a real about page.

## Old deploy

`.gitlab-ci.yml` still builds Jekyll to `public/` on `master` for GitLab Pages. Domain DNS (Porkbun) points `tayloramurphy.com` at GitLab Pages. The Let’s Encrypt cert for the custom domain expired 2026-04-09.

GitHub Pages at `tayloramurphy.github.io` is a separate, older build and is not the custom domain.
