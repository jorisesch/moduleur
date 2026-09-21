# Official Shmoergh source repositories

These are independent Git clones of the public repositories published by
[Shmoergh on GitHub](https://github.com/shmoergh). They were cloned on
2026-09-20, including all 10 repositories available at that time except `hog`,
which was intentionally excluded.

Each clone has its own Git history and an HTTPS `origin` remote pointing to
`https://github.com/shmoergh/<repository>.git`.

## Sources

- [brain-basic-midi2cv](https://github.com/shmoergh/brain-basic-midi2cv)
- [brain-cv-tuner](https://github.com/shmoergh/brain-cv-tuner)
- [brain-cv-utils](https://github.com/shmoergh/brain-cv-utils)
- [brain-diagnostics](https://github.com/shmoergh/brain-diagnostics)
- [brain-firmwares](https://github.com/shmoergh/brain-firmwares)
- [brain-sdk](https://github.com/shmoergh/brain-sdk)
- [kicad-libs](https://github.com/shmoergh/kicad-libs)
- [le-controlleur](https://github.com/shmoergh/le-controlleur)
- [lo-fi-delay](https://github.com/shmoergh/lo-fi-delay)
- [moduleur](https://github.com/shmoergh/moduleur)

Only this README and `refresh.sh` are shared in Git; all official clones are
ignored. In particular, `upstream/moduleur/` is an independent official source
clone and is not part of this repository's history.

## Refresh one repository

Run these commands from this `upstream/` directory, replacing `brain-sdk` with
the desired repository name:

```sh
git -C brain-sdk status --short --branch
git -C brain-sdk fetch origin --prune --tags
git -C brain-sdk pull --ff-only
```

Check that the working tree is clean and you are on the branch you intend to
update before pulling. Fetch downloads upstream commits and tags without
changing your checked-out files. Pull updates the current branch from its
configured tracking branch. `--ff-only` refuses divergent history instead of
creating a merge commit.

If you have local work, commit it on your own branch or stash it before updating.
If a pull fails, inspect the reported problem rather than resetting or discarding
local changes.

## Refresh all existing clones

Run [refresh.sh](refresh.sh) from this `upstream/` directory:

```sh
./refresh.sh
```

You can also invoke it from any working directory; it always finds clones beside
its own file. It requires Git and network access.

The script skips repositories with local changes (including untracked files),
detached HEADs, or no tracking branch. For each remaining clone, it fetches from
`origin` with pruning and tags, then runs `git pull --ff-only` on the current
tracking branch. It does not switch branches or discard local work.

Failures are reported individually and the remaining repositories are still
processed. The script exits nonzero if inspection, fetching, or pulling fails;
intentional skips are reported but do not count as failures. If a branch has
diverged, inspect it and resolve the situation manually before retrying.

## New repositories and release downloads

Refreshing clones does not discover new GitHub repositories. Check the
[Shmoergh repository list](https://github.com/shmoergh?tab=repositories)
occasionally and clone any new projects you want from this directory:

```sh
git clone https://github.com/shmoergh/<repository>.git
```

Git pulls also do not download GitHub release attachments or refresh the files in
`../downloads/`. Obtain firmware archives and patch sheets separately using the
[official downloads links](https://www.shmoergh.com/guides/moduleur-user-guide/#downloads),
or run `../downloads/refresh.sh` to update the local downloads and preserve changed files.
