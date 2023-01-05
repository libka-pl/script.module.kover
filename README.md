# kover

Simple Kodi **Ver**sion unification proxy. Keeps K19 and K20 API available together.

It's useful if you:

- have a K19 plugin and you want to run it on K20 without thousands of warnings
- have a K20 plugin and you want run it on K19
- want to port K19 plugin to K20 but you don't heave a time, and you port file by file

Kover implements K19 and K20 API at the same time.


## Usage

Just import auto installer to patch all `xbmc*` modules. Put it on top of your main plugin script.
```python
from kover import autoinstall  # noqa: F401
```

Next use The Kodi API as ususal.


## Repo

The `kover` module is avaliable in the `libka` repository – https://repo.libka.pl/repository.libka.zip


## To-do list

- [x] list items
- [ ] settings
