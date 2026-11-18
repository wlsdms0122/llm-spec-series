# Guide

## What a specification is

A specification is where a project keeps what it has decided, as a series of specs. It is how the project is managed, the way issues and commits are, and it is kept for as long as the project is: it is not a requirements document written once before the work and left behind. A spec can decide anything the project has to hold to: a design, a rule, an interface, a process. The principles below are the package's. The details are each project's to shape.

1. **A decision is not rewritten. It is replaced.** A spec is made clearer in place while what it decides holds. When what it decides has to change, a new spec supersedes it whole, and the old one stays, marked on its head as superseded and by what. The history is kept, what no longer holds is plain where it is read, and the new spec says what holds instead.
2. **What counts is worked out, never written.** The live set is every accepted spec no accepted spec supersedes. No list of it is kept by hand, so no list can disagree with the specs.
3. **A spec explains.** Its folder holds its text and the resources only it needs, such as the cases that measure it. Tools and code the project uses elsewhere live where the project keeps them.
4. **A spec may be measured.** Where its rules can be checked, cases hold them and a run says whether the work passes. Where they cannot, a review judges the text alone. Both are verification, and a spec has the kind its rules allow.
5. **What a tool can decide, a tool decides.** The shape of each spec, the links, the numbers, the live set and the places a change reaches are computed. Judgement is spent only on what is left: whether the work is the project's, whether the rules are right, whether the cases are enough.
6. **A decision is reviewed before it counts.** A draft is accepted when it meets the project's acceptance criteria, and a review answers each one with evidence.

## How a specification is laid out

```
spec/
  README.md       what the system is, how the specification works, how it is measured
  review/         how a spec is reviewed, and a record of each run
  TEMPLATE.md     spec/ is a series when it holds a template
  APP-1/
    SPEC.md
    <resources>/
  ops/            a folder that holds a template is a series too
    TEMPLATE.md
    OPS-1/
```

A series is a folder that holds a `TEMPLATE.md`, and its template's prefix is its key, so `OPS-1` names one spec in the whole specification. A project has as many series as it has kinds of decision that are shaped differently, each with its own template, and every series shares the README and the review. A spec may supersede a spec of any series.

`init` writes the README, the review and the first template once, and `init` again with another prefix and `--folder` writes another template. From then on they are the project's documents. The written `spec/README.md` states the rules of the specification, and this guide does not restate them.

## The template is what the tools ask

- The prefix is the one the template's heading writes.
- The head fields are the lines under the template's heading, in that order. `Status` must be among them, since whether a spec counts is read from it. `Supersedes` is read for supersession when it is there, and a series whose specs can be superseded declares `Superseded-By`, which `accept` writes. Any other field the template declares, such as `Implementation: <link>`, a spec may write, in the template's order. A series that is released declares `Release`, which `release` writes. `draft` copies every declared field but those three.
- The sections are the template's `##` headings. Rename, add or remove one, and every spec of the series is held to the new list.

What is not in the template is not checked. Resources are a spec's own, so no tool asks that a spec has cases, and the review's criteria say which series are measured.

## How a spec moves

1. `draft` starts a spec under the next number of its series. It is changed freely while it is a draft.
2. If it changes accepted specs, the changes are made beside it. `impact` prints the places in the live set the draft reaches, and `lint --as` prints each link its acceptance would leave on a superseded spec.
3. A review judges it against the criteria.
4. `accept` sets its status and writes `Superseded-By` into each spec it supersedes. It refuses while `lint --as` finds anything.
5. When the project cuts a release, `release <name>` writes `Release: <name>` into every accepted spec that names none, so a spec says which release it entered. It refuses while `lint` finds anything.
6. From then on it is supplemented in place, or superseded whole by a new spec.

`list --live` gives the system as it stands, and `list --live --as <KEY>` gives it as a draft would leave it. `history <KEY>` gives where a spec stood in each release, read from the repository's tags: the release it entered, and each after where it was superseded.

## How a review runs

`spec/review/README.md` is the procedure: a coordinator, reviewers each with one scope, a ledger judged row by row, and a verdict. The coordinator runs every tool first, then hands each reviewer one file from `pack`: the brief, the criteria it answers, the scope whole with its resources, the sections the scope links to, and what the tools printed. A reviewer reads that file and writes its report and its probes where the pack says. So every reviewer is briefed in the repository's words, reads once, and spends its judgement on what no tool could decide. Where a run has many scopes, a verifier briefed by `review/VERIFIER.md` drafts each scope's ledger, and the coordinator judges what it rejects or puts to the owner.

What a run keeps is one record in `spec/review/record/`, started by `record`: the commit, the scope, the verdict, the criteria table, and a line for each finding deferred, rejected or put to the owner.

## Shaping it to a project

The written documents are a full specification process, and a project keeps what it needs. Each place left for the project is an HTML comment in a written document: what the system is (the reviewers judge criterion A by it), which series are measured and how a case is written and run, the stages it refuses at, the order to read the specs in, and the criteria that say what is the system's own to decide. The review's modes, the coordinator's steps and the criteria are prose, and the project changes them as it learns. A criterion a project drops is one its reviewers stop answering.

## What the tools check and compute

`lint` checks:

- each spec's head: the heading, the declared fields in order, the status
- what it supersedes: a spec of the specification, accepted, not itself, named once, and no supersession running in a circle
- that a spec writes `Superseded-By` exactly when accepted specs supersede it, naming each of them once
- that a draft writes no `Release`, and a `Release` names one release in one word
- each spec's sections, against its series' template
- that an accepted spec has nothing marked **Open.**
- that every folder in `spec/` is `review/`, a series or a spec, and every prefix names one series
- that every inline and reference link in the specification's documents resolves, stays in the repository, and does not reach a superseded spec from the live set

`draft` takes one more than every number of the series in its folder and in the repository's git history, so a deleted draft's number is not used again. `impact` reads the draft and each spec it supersedes, and prints each live line that links to a superseded spec or shares with them a code span or a run of six words few live documents write: places to look, which the review judges. `record` writes the commit only when `spec/` has no change left uncommitted.
