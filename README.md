# spec-series

Use this to keep what a project decides as a specification: a series of numbered specs, each replaced by a new one rather than rewritten, each reviewed against the project's criteria before it counts, and measured by cases where its rules can be checked. The package states the principles, writes a full specification process into a project once, and gives the tools that decide whatever needs no judgement.

This directory is an open-package. The specification is `open-package spec`.

## Using it

Paths are absolute, since commands run from the package root.

```
open-package init <repository> --prefix APP --name App [--folder app]   # a series, and on the first the README and review/
open-package draft <repository> "<title>" [--prefix APP]                 # a draft under the next number of the series
open-package accept <repository> APP-7                                   # a judged draft, once it lints as accepted
open-package release <repository> 1.2                                    # the release into each accepted spec that names none
open-package history <repository> APP-7                                  # where a spec stood in each tagged release
open-package list <repository> [--live] [--as APP-7]                     # every spec and its status, or the live set
open-package lint <repository> [--as APP-7]                              # exit 1 with a line per finding
open-package impact <repository> APP-7                                   # the live lines a draft reaches
open-package pack <repository> <mode> APP-7 ... [--criteria ABDE]        # one reviewer's reading, in one file
open-package record <repository> <mode> APP-7 ...                        # a review run's record, started
open-package test                                                        # the package's own tests
```

[The guide](document/GUIDE.md) gives the principles, the layout, how a spec moves and is reviewed, and how a project shapes the written documents to itself.
