# Reviewing the specification

How a draft is reviewed before it is accepted, and how what is accepted is audited. What decides acceptance is [the acceptance criteria](CRITERIA.md). A run has one coordinator and several reviewers. The coordinator follows this page and hands each reviewer a pack, one file written from this repository: [the reviewer's brief](REVIEWER.md), the criteria it answers, its scope and what was run beforehand. A workflow runner, or anything that can start agents and hand them a file, can coordinate, so the review travels with what it reviews.

## Modes

| mode | what is reviewed | when |
|---|---|---|
| `draft` | one draft, with the changes it makes in accepted specs and the places in the live set it reaches | before it is accepted |
| `change` | a diff to accepted specs | before a supplement or a superseding spec is merged |
| `series` | the live set, or one series of it, split into scopes | after a release, or when the owner asks |

The input of a run is the mode, the specs or the diff, and the commit of this repository it reads.

## Scopes

A reviewer reads one scope, and a scope is small enough to read whole: one draft for `draft`, the specs a diff touches for `change`, and a run of neighbouring specs for `series`. A spec outside the scope is read only at the sentence the scope links to, and the pack holds that section. For `series`, the coordinator cuts the live set into scopes of related titles, in reading order, from the live set at the commit.

What a reviewer pays for is its reading. The brief, the criteria and how the specification works are read by every reviewer, so a scope is as large as one reading holds, about ten specs, rather than many small scopes that each pay that again. A scope goes to two reviewers, one answering every criterion but C and the other C, only where its resources are too many to read beside its text.

## The coordinator

1. Check what the specification's rules decide without judgement: each head and its fields, the sections, what supersedes what, and the links. A run starts from a specification that holds, since none of that needs a reviewer.
2. Run beforehand what needs no judgement, so that no reviewer spends its reading on it. For `draft`, the diff of `spec/` from where the draft branched gives the changes it makes in accepted specs, step 1 run as if the draft were accepted gives each link its acceptance would leave pointing at a superseded spec, and the places in the live set the draft reaches are each live line that links to a spec it supersedes or repeats their words, which the pack also holds. Where the scope is measured, run every case of the scope on the reference implementation. For `change`, run the whole suite before and after the diff and compare the two: an answer that moved makes the change a supersession, not a supplement.
3. Start the record. It names the commit, and a run reads a commit only while `spec/` has no change left uncommitted, since otherwise no commit is what the run reads.
4. Write one pack per reviewer: the brief, the criteria it answers, `spec/README.md`, the record lines of its scope, the scope whole with its resources, the sections the scope links to, the output of step 2, and where its report and probes go. Start each reviewer with its pack and nothing else. Every reviewer of every run is briefed in the same words, from this repository.
5. Run the probes the reviewers wrote, each a file in the case format, the way step 2 ran the cases. Then verify every critical and major finding before it reaches the ledger: re-derive the reasoning from the spec text and the cases, not from the reviewer's words, and confirm a finding about behaviour by the line a run printed. A minor finding is verified by reading.
6. Merge findings with one root into one row.
7. Judge each row: **adopt** (fix it now), **defer** (record it and fix it when that spec is next touched), **reject** (no change, with the reason), or **owner** (a real design fork). A finding an accepted rule already settles is the coordinator's to judge. An owner row goes to the owner as a question: the subject, a concrete example and what it answers, and every noun defined.
8. Write the ledger, the run's working table: one row per finding, with id, criterion, spec, claim, severity, evidence, verdict, reason, and for an adopted row whether the fix is a supplement or a superseding spec. Then answer every criterion for the whole run, yes, no or unchecked, with the evidence. A criterion two reviewers answered differently is settled by the coordinator running it.
9. Give the run's verdict, accept, revise or reject, as CRITERIA.md defines them. For `draft`, the verdict is what the owner reads to decide, and where the draft is measured, accepting also needs the reference implementation to pass its cases (criterion C5).
10. Fixes run after the owner has read the ledger: the spec and its resources first, then each implementation. A draft the owner accepts is accepted once step 1, run as if it were, holds, and each spec it supersedes then writes `Superseded-By`.
11. Fill in the record: the verdict, the criteria table, and under it one line for each finding judged defer, reject or owner, with its id, criterion, spec, claim, verdict and reason. An adopted finding is not recorded, since its fix is in the text and the history. A deferred line is deleted when its fix lands, and an owner line when the answer is in the text. A rejected line stays, so the same finding is not raised again unless its reason fails. The ledger is not kept.

Where a run has many scopes, the coordinator may hand steps 5 to 8 of each scope to a verifier, briefed by [the verifier's brief](VERIFIER.md) with that scope's reports, the lines its cases and probes printed, and where its ledger goes. The coordinator then judges every reject and owner row itself, merges the scopes' ledgers into the run's, and keeps its own notes where no reviewer reads.

A round ends when what is left is wording and maintainability. Critical and major findings start another round on the fixes alone, and only where a fix could reach further than its own lines.
