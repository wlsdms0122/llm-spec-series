# {{PREFIX}}-N: Title

Status: draft
Supersedes: {{PREFIX}}-a, {{PREFIX}}-b
Superseded-By: {{PREFIX}}-c
Release: 1.0

<!--
The shape of a {{PREFIX}}'s SPEC.md. A {{PREFIX}} starts as a copy of this file under the next number, with no field but its Status.

- The heading and the Status line are required. Supersedes is written only by a spec that replaces others whole, and it may name specs of any series. Superseded-By is written into a replaced spec when the spec replacing it is accepted, and names every accepted spec that supersedes it, once each. Release is written into an accepted spec when the release it enters is cut. A draft writes neither.
- The lines under the heading are the fields a {{PREFIX}}'s head may write, in this order. Add a field here, and a {{PREFIX}} writes it when it applies.
- Every section below is written in every {{PREFIX}}, in this order. A section with nothing to say keeps its heading and is left empty. Rename, add or remove one here, and every {{PREFIX}} is held to the new list.
- Rules is the only normative section. Everything else explains it and binds nothing.
-->

## Summary

One paragraph: what this {{PREFIX}} adds to {{NAME}} or decides about it, for someone reading it first.

## Motivation

Why this is {{NAME}}'s to do and not its users' or a neighbour's. Name what could not be done with the live set alone, or what two people doing the work would do differently without it, and show it with a concrete example.

## Rules

The normative text. Every sentence here is one the work follows, and where the series is measured, each is held by a case. Subsections (`###`) by construct, as the rules need them. A `**Note.**` paragraph may stand beside the rule it is about, and binds nothing. A form (a name, a spelling, a field, a layout) is given whole as a grammar or a table, and each rule says what a thing is, never only the one input that raised it.

## Interactions

Where these rules meet what the live set already has. A rule another spec states is linked to, not restated.

## Alternatives considered

The designs not taken, each with the rule or principle that set it aside.

## Notes

`**Note.**` paragraphs about the {{PREFIX}} as a whole: what it costs the work, and what no case can hold.
