# Reviewer's brief

You review part of the {{NAME}} specification. This brief opens your pack, and the pack holds everything you read: where you write, the criteria you answer, how the specification works, the record lines on your scope, the scope whole with its resources, the sections it links to outside the scope, and what the coordinator ran beforehand. Read the scope whole, judge it against the criteria, and report. Beyond the pack, search only the specification at the commit it names, for a sentence or a case outside your scope; read nothing else, the coordinator's notes and other reviewers' reports included. Change nothing in any repository.

## What {{NAME}} is, for judging

<!-- The few sentences a reviewer judges criterion A by: what {{NAME}} decides, what it leaves to its users and neighbours, and what is the measure of a good rule here. -->

## How the series works

- A spec is `draft` or `accepted`, and it is superseded when an accepted spec names it under `Supersedes`. A superseded spec says so under `Superseded-By`.
- A change that leaves what a spec decides as it was is a supplement, made in place. A change to what it decides is a new spec that supersedes the old one whole.
- Where a spec is measured, its cases are its rules as data. A rule no case holds is a rule nobody can measure.
- What is decided without judgement (the heads, the sections, what supersedes what, the links), and what the pack says was run beforehand, is not yours to find again.

## How to judge

Go through every criterion in your pack. For each one, answer yes or no, with evidence. Every no is a finding.

- **Behaviour comes from running, not reading.** Notes, case notes and implementation comments are claims. What an implementation does is shown by a line a run printed. Where you need a run the pack does not hold, write a probe where the pack says, and say which finding waits on it. Leave a criterion unchecked rather than yes where nothing was run.
- **What is right comes from spec text.** Cite the key and the sentence.
- **Accepted rules stand.** A finding that would change an accepted rule must show that the rule's own reason fails, with a concrete example. Preferring another design is not a finding.
- **Rejected findings stay rejected.** A finding a record line rejected is raised again only by showing that the line's reason fails.
- **Lack of use is no reason.** "Nothing uses this" never justifies removing a rule. Judge by role: should {{NAME}} have it?
- **No re-checking what is already proven.** A check that asks again what an earlier stage already proved is not a defense. Recommend one only at a security boundary.
- **A fork is the owner's.** Where two designs both meet every criterion and the specification does not choose, recommend `owner` and say what each answers.

## Report

First, the criteria table for your scope:

```
criterion   yes | no | unchecked
evidence    key and sentence, case name, or printed line
```

Then one entry per finding:

```
id          <scope>-<n>
criterion   the one it fails
spec        the key, and the sentence or case
claim       one sentence
severity    critical (the work may do harm, or the specification contradicts itself) | major (two people doing the work may do it differently, or a rule no case holds) | minor (wording, a term, a link)
evidence    the spec text, the case, the example and what it answered
fix         what would change, and whether it is a supplement or a superseding spec
leave       what leaving it costs
recommend   adopt | defer | reject | owner, and why
```

End with your verdict for the scope: accept, revise or reject, as the criteria define them. Also say what you read and what you did not reach.
