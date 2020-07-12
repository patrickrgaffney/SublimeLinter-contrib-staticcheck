# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## v1.0.0 - 2020-07-12

### Fixes

- Catch and report "could not analyze errors". These typically occur when a dependency cannot be resolved. Previously they were not being reported.

### Refactor

- Parse the JSON output of `staticcheck` instead of using a regex to parse the CLI text output.

## v0.1.0 - 2019-12-17

Initial public release.
