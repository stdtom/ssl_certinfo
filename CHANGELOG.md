# Changelog

## v1.1.0 (2020-10-03)

#### New Features

* Read proxy url from environment variable
* Add support for http proxy
* Add parsing and checking of proxy urls
#### Fixes

* Update dependencies
#### Refactorings

* merging if statement in parse_proxy_url
#### Docs

* Update README.rst
#### Others

* Change classifiers in pyproject.yaml
* Add test to unset env variable with empty option
* Fix proxy env priority test for win32 platform
* Add  testing of -x parameter
* Setup proxy server for testing
* Refactoring setup of webserver for testing

Full set of changes: [`v1.0.0...v1.1.0`](https://github.com/stdtom/ssl_certinfo/compare/v1.0.0...v1.1.0)

## v1.0.0 (2020-08-29)

#### New Features

* Add multiple output formats
* Add option --version
#### Docs

* Provide basic documentation in README.rst
* Updateing contribution notes
#### Others

* fix breaking change from isort 5.0.x

Full set of changes: [`v0.3.5...v1.0.0`](https://github.com/stdtom/ssl_certinfo/compare/v0.3.5...v1.0.0)

## v0.3.5 (2020-07-26)

#### Others

* Add pyinstaller to bundle into a stand-alone executable
* Build stand-alone executable and deploy to GitHub Releases
* Move deployment to separate stage; Add Windows job to test stage
* Fix tests failing on windows
