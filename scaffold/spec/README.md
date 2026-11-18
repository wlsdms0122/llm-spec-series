# The {{NAME}} specification

This is where what is decided about {{NAME}} is kept. Whatever is built or done for {{NAME}} follows it, and nothing that work does adds to it. Where a decision lands a cost on the work, or where it cannot be measured, the spec that makes the decision says so in a **Note.**, so whoever does the work next is told rather than left to find it.

<!-- Say which version of {{NAME}} this describes, in bold, on a line of its own. -->

## What {{NAME}} is

<!-- What {{NAME}} is for, in one sentence, and every property that follows from it. A reviewer judges whether work is {{NAME}}'s to do against this section, so it says what {{NAME}} decides and what it leaves to its users and its neighbours. -->

## How the specification works

The specification is a record of decisions, kept as specs. A spec is not rewritten once it is decided. When what it decides has to change, a new spec replaces it, and the old one stays where it was: what held before is still there to read, it is plain that it no longer holds, and the spec that replaced it says what holds instead. So the specification is also the project's history, and it can be read in the order things were decided.

A spec belongs to a series. A series is a folder that holds a `TEMPLATE.md`, and the template gives the series' prefix, the fields a spec's head may write and the sections every spec holds. `spec/` is a series itself when it holds a template, and each folder in it that holds one is a series too. Beside its series, `spec/` holds this page and the review in [`review/`](review/README.md), and nothing else.

A spec is a folder `<PREFIX>-N/` in its series: its `SPEC.md`, and beside it, in folders, the resources only that spec needs, such as the cases that measure it. What the project uses everywhere, its tools and its code, is not a spec's to hold. `<PREFIX>-N` is the spec's key and names it across the specification. N is the next number free in the series when the spec is drafted, it is never used again, and it says nothing else about the spec.

A `SPEC.md` opens with `# <PREFIX>-N:` and its title, then the fields its template declares, in the template's order. Status is always written:

- **`draft`**: proposed, not decided. It is changed freely and nothing is held to it. A draft that is not accepted is deleted.
- **`accepted`**: decided. A draft is accepted when it meets [the acceptance criteria](review/CRITERIA.md), which a review checks one by one.

Every `SPEC.md` holds every section of its template, in order, and a section with nothing to say is left empty.

**How a rule is written.** A rule gives a form whole, the way a drawing gives a part's dimensions and not only its material. What a name, a spelling, a field or a layout may be is a grammar or a table, and the prose beside it says what each part means. A rule says what a thing is. It is not written against the one input that raised it: that input is a case, and why the form is what it is goes in a **Note.**

**Supplement or supersede.** An accepted spec is supplemented in place while what it decides stays as it was: its prose made clearer, its resources added to or corrected. Where it has cases, that means every case keeps its answer. A change to what it decides is not a supplement. It is a new spec that replaces the old one whole and says so on the line after its status, `Supersedes: <KEY>, <KEY>`, naming specs of any series. Nothing replaces part of a spec. A spec is superseded when an accepted spec names it under `Supersedes`, and when that spec is accepted, the superseded one says so on its own head, `Superseded-By: <KEY>`, so whoever opens it sees at once that it no longer holds. Its text is not touched. The two always agree: a spec writes `Superseded-By` exactly when accepted specs name it under `Supersedes`, and names each of them once. Until {{NAME}}'s first release, an accepted spec is changed in place even when what it decides moves.

**Release.** When {{NAME}} is released, each spec accepted since the release before says on its head which release it entered, `Release: <release>`, so whoever opens it sees when its rules began to hold. The line is written when the release is cut, and a draft has none. The repository's tags stay the record of what each release held, and a spec stopped holding at the `Release` of the spec that superseded it.

A draft makes the changes it needs in accepted specs beside it, before it is reviewed: a supplement in place, and a spec whose decision moves named under its `Supersedes`. The review reads the draft with those changes.

{{NAME}} as it stands is every accepted spec that no accepted spec supersedes, the live set. Which specs those are is worked out from the heads and never written down. The specification is kept the way spec-series keeps one, and its tools check and write what this page decides without judgement.

<!-- Say in which order the specs are best read, by area. The numbers give arrival, not that order. -->

## Conformance

A spec may be measured. Where its rules can be checked, its cases hold them, and whether the work conforms is a fact a run prints and never a judgement. Where they cannot be checked, the review judges the spec by its text alone.

**must / must not** are requirements. **refuses** means the implementation raises an error naming what was wrong and produces nothing else: no partial result, no best guess.

**Note.** A paragraph opening with **Note.** is not a requirement. It says what a rule is for, what an implementation is likely to get wrong, or what the rule would cost written another way. Removing every one of them removes nothing the work is held to, and no case measures one.

The cases are the rules written as data. A case has a name, a note saying which rule it measures and how, an input, and what is expected of it: an answer, or a refusal at a stage. One case breaks one rule, and its note says which. A runner reads each case, gives its input to the implementation, and compares what comes back with what is expected. An implementation that pins a version of this specification conforms to it when it passes the cases of every live spec at that version.

<!-- Which series are measured and which are judged by their text alone. For a measured series: the format a case is written in, the folder beside each SPEC.md that holds them, and the runner that reads them. Where {{NAME}} refuses or fails at more than one stage and the stage is part of the behaviour, name the stages and the names the cases use for them. -->
