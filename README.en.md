---
date created: 2026-04-18
date modified: 2026-10-24
tags: [소개]
---

[한국어](README.md) | English

# writing-style

A workspace that researches, reviews, and specifies the formal rules for all of the user's (Arngard's) writing. It covers every genre: plain-prose records (documents, reports), retrospectives, creative writing such as fiction, code comments, and commit messages. Writing rules kept elsewhere, such as the user's common guidelines and the scaffold's document-writing rules, are short-form rules applied to each task; this repository holds the formal rules, with their rationale and complete specification.

## When revising text against this repository

An agent revising text in another repository reads in this order.

1. Determine the genre of the text from [_docs/_ontology/writing-genres.md](_docs/_ontology/writing-genres.md).
2. Find and apply the rules for that genre through the file guide in [_docs/_architecture/AGENTS.md](_docs/_architecture/AGENTS.md). Plain-prose records follow [_docs/_architecture/plain-prose-rules.md](_docs/_architecture/plain-prose-rules.md).
3. For details such as usage and notation, see the example-based detailed rules in [_implementation/](_implementation/AGENTS.md).
4. When the reason for a rule is needed, see the rationale documents in [_docs/_strategy/](_docs/_strategy/AGENTS.md).

The target of revision is the text in that repository; this repository is read only. If this repository's rules and the short-form rules the target repository follows disagree, raise it with the user before revising. If you find something to fix in this repository's rules, hand it over as work for this repository.

## Structure

This repository inherits the epistemic workspace scaffold ([arngard/epistemic-workspace-scaffold](https://github.com/arngard/epistemic-workspace-scaffold)) as `upstream`. What each area holds is set by [_docs/_architecture/category-placement.md](_docs/_architecture/category-placement.md).

| Area | Holds |
|------|-------|
| `_docs/_ontology/` | Definitions of writing genres and writing concepts |
| `_docs/_knowledge/` | External facts, reviews of external writing guidelines, the user's stated writing preferences |
| `_docs/_strategy/` | Rationale for the rules, rejected alternatives, retrospectives |
| `_docs/_architecture/` | The formal rules for each genre |
| `_implementation/` | Example-based detailed rules |

The single entry point for operating guidelines is [AGENTS.md](AGENTS.md).
