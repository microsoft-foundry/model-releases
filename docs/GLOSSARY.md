# Glossary

Short, linkable explainers for terminology used across capsules,
notebooks, and primers. Every term is a level-3 heading so it produces
a stable kebab-case anchor you can link to from anywhere:

```markdown
See [context window](../docs/GLOSSARY.md#context-window).
```

Managed by the [`add-to-glossary`](../.github/skills/add-to-glossary/) skill.
Rules for every entry:

- Filed under the correct **letter section** below.
- **Alphabetized** within its section, level-3 heading (stable kebab-case anchor).
- **2–4 sentences** — short by design.
- **At least one grounding reference**, ideally on
  [Microsoft Learn](https://learn.microsoft.com/). Fall back to the
  provider's official docs only when Learn does not yet cover the term.
- Added **on demand** — when a term first shows up in a capsule or
  primer, or on user request. Do not pre-populate.

**Jump to:**
[A](#a) · [B](#b) · [C](#c) · [D](#d) · [E](#e) · [F](#f) · [G](#g) ·
[H](#h) · [I](#i) · [J](#j) · [K](#k) · [L](#l) · [M](#m) · [N](#n) ·
[O](#o) · [P](#p) · [Q](#q) · [R](#r) · [S](#s) · [T](#t) · [U](#u) ·
[V](#v) · [W](#w) · [X](#x) · [Y](#y) · [Z](#z)

---

## A

_No entries yet._

## B

_No entries yet._

## C

### Context Window

The maximum number of tokens a model can consider at once — including
your prompt, the conversation history, retrieved documents, and the
model's own reply. When you exceed it, older content is truncated or
must be summarized. "Long context" models push this into the hundreds of
thousands of tokens; most chat models sit in the tens of thousands.

**Reference:** [Work with chat completion models — Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/chatgpt)

## D

_No entries yet._

## E

_No entries yet._

## F

_No entries yet._

## G

_No entries yet._

## H

_No entries yet._

## I

_No entries yet._

## J

_No entries yet._

## K

_No entries yet._

## L

_No entries yet._

## M

### Model Optimization

A continuous improvement loop that iteratively moves an application toward
its cost, quality, and latency goals by pulling on a set of levers —
model selection, prompt optimization, context engineering, evaluation,
fine-tuning, quantization, and distillation — rather than a one-time
configuration step. Each iteration measures progress against target metrics
and feeds results back into the next round of adjustments.

**Reference:** [A Developer's Guide to Managing Models, Cost and Quality in Microsoft Foundry](https://devblogs.microsoft.com/foundry/build-2026-foundry-models/)

## N

_No entries yet._

## O

_No entries yet._

## P

_No entries yet._

## Q

_No entries yet._

## R

_No entries yet._

## S

_No entries yet._

## T

_No entries yet._

## U

_No entries yet._

## V

_No entries yet._

## W

_No entries yet._

## X

_No entries yet._

## Y

_No entries yet._

## Z

_No entries yet._

<!--
Adding a term:
1. Find its letter section above.
2. Insert alphabetically, using a level-3 heading (### Term Name).
3. Write 2–4 sentences.
4. End with **Reference:** <link> — ideally to learn.microsoft.com.
5. Replace the section's "_No entries yet._" placeholder if it was empty.
-->
