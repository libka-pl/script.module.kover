# kover

Simple **Ko**di **Ver**sion unification proxy. Keeps K19 and K20 API available together.

It's useful if you:

- have a K19 plugin and you want to run it on K20 without getting thousands of `ListItem.setProperty() is deprecated` warnings
- have a K20 plugin and you want run it on K19
- want to port K19 plugin to K20 but you don't have a time, and you port file by file

Kover implements K19 and K20 API at the same time.


## Usage

1. Add `kover` as an addon dependency in `addon.xml`:
```xml
<import addon="script.module.kover" />
```

2. Import auto installer to patch all `xbmc*` modules. Put it on top of your main plugin script.
```python
from kover import autoinstall  # noqa: F401
```

3. Next, use Kodi API as usual.


## Repo

The `kover` module is avaliable in the `libka` repository – https://repo.libka.pl/repository.libka.zip


## To-do list

- [x] list items
- [ ] settings
