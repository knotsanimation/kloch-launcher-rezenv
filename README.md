# kloch_rezenv

![Made with Python](https://img.shields.io/badge/Python->=3.7-blue?logo=python&logoColor=white)

Launcher plugin for [Kloch](https://github.com/knotsanimation/kloch) implementing support for [rez](https://rez.readthedocs.io).

# installation

See https://knotsanimation.github.io/kloch/launcher-plugins.html for installation.

# usage

Defines 3 options:

- `requires`: mapping of package name / package version
- `params`: see https://rez.readthedocs.io/en/stable/commands/rez-env.html
- `config`: build a valid yaml rez config, see https://rez.readthedocs.io/en/stable/configuring_rez.html


Example in a profile:

```yml
__magic__: kloch_profile:4
identifier: demo
version: 0.1.0
launchers:
  rezenv:
    requires:
      testpkg: 1.2.3
    params:
      - "-vvv"
  rezenv@os=windows:
    config:
      default_shell: "powershell"
```
