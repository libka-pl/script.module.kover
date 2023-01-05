# kover

Simple Kodi **Ver**sion unification proxy. Keeps K19 and K20 API available together.

It's useful if you:

- have a K19 plugin and you want to run it on K20 without thousands of warnings
- have a K20 plugin and you want run it on K19
- want to port K19 plugin to K20 but you don't heave a time, and you ports file by file

Kover implements K19 and K20 API at the same time.


## Usage

Just import auto installer to patch all `xbmc*` modules.
```python
from kover import autoinstall  # noqa: F401
```

Next use The Kodi API as ususal.


## Repo

The `kover` module is avaliable in the `libka` repository – https://zip.libka.pl/pool/20/repository.libka/repository.libka-0.9.zip

The last version can be found at the location – https://zip.libka.pl/pool/20/script.module.kover/


## To-do list

- [x] list items
- [ ] settings
