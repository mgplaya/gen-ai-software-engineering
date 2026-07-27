# Skill: Research Quality Measurement

**ID**: `research-quality-measurement`
**Used by**: `agents/research-verifier.agent.md` (Stage 1)
**Purpose**: Give the Research Verifier a single, objective rubric for stating how
trustworthy a piece of bug research is, and a fixed shape for the result file.

---

## When to apply

Apply this skill whenever you write `verified-research.md`. The research-quality
rating in that file MUST use one of the levels defined below — never ad-hoc wording
like "looks good" or "mostly fine".

## Quality Levels

Rate research on a 4-level scale. Assign the level using the decision rule below.

| Level | Label | Meaning |
|-------|-------|---------|
| **A** | Verified | Every `file:line` reference resolves and every quoted snippet matches the source byte-for-byte (whitespace-insensitive). No fabricated claims. Root-cause explanations are consistent with the code. |
| **B** | Mostly Verified | All *material* claims (the ones a fix depends on) are correct, but there are minor discrepancies: a line number off by a few, a paraphrased-but-accurate snippet, or a missing reference for a non-critical claim. |
| **C** | Partially Verified | At least one material claim is wrong or unverifiable (wrong file, snippet that does not exist, root cause that contradicts the code), but at least one material claim still holds. A planner must not act on the unverified parts. |
| **D** | Unverified / Unreliable | Most claims fail verification, references are fabricated, or the research is empty. The planner must NOT proceed on this research. |

### Decision rule (apply top to bottom, stop at first match)

1. If there is no research content to check → **D**.
2. If any *material* claim (one a fix directly depends on) is factually wrong or its
   reference/snippet cannot be found in the source → **C** (or **D** if the majority
   of material claims fail).
3. Else, if only non-material discrepancies exist (off-by-few line numbers,
   paraphrased snippets, missing non-critical refs) → **B**.
4. Else (everything checks out exactly) → **A**.

A "material claim" is one that a downstream fix would rely on: the buggy file, the
buggy line/function, and the described root cause. Cosmetic details (surrounding
comments, exact blank lines) are non-material.

## Required result-file sections

`verified-research.md` MUST contain exactly these sections, in this order:

1. **Verification Summary** — one line: `PASS` or `FAIL`, plus the Research Quality
   level (A/B/C/D + label). `PASS` requires level A or B.
2. **Verified Claims** — a table: claim, `file:line`, "match" / "mismatch", note.
   Every claim from the research must appear here.
3. **Discrepancies Found** — each discrepancy: what the research said, what the
   source actually says, and whether it is material.
4. **Research Quality Assessment** — the level (A/B/C/D), and 2–4 sentences of
   reasoning that explicitly reference the decision rule above.
5. **References** — the exact `file:line` locations checked, so a planner can jump
   to them.

## Verification procedure

For each claim in `codebase-research.md`:

1. Open the referenced file at the referenced line.
2. Confirm the file exists and the line is within range.
3. Compare the quoted snippet to the actual source (ignore leading/trailing
   whitespace; flag substantive differences).
4. Sanity-check the stated root cause against the code's actual behavior.
5. Record match/mismatch and whether any mismatch is material.

Never "verify" a claim you did not actually open the source to check.
