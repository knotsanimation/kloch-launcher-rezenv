# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2025-01-??

### fixed

- rez-env subprocess execution on UNIX system

### changed

- the launcher will now raise if it can't find a path to the `rez-env` executable
  using `shutil.which`.

### chores

- added e2e tests which actually call rez