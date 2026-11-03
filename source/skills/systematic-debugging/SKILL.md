---
name: systematic-debugging
description: Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes
---

# Systematic Debugging

Find the cause from evidence before changing behavior. Match the depth of the
investigation to the problem; a clear local failure does not need a formal
incident process. Use the following phases to avoid speculative fixes.

Honor analysis-only requests throughout these phases: inspect permitted evidence
and recommend tests or fixes without changing files, adding diagnostics, or
performing other mutations. Hypothesis testing and implementation steps apply
only within the authorized task; stop at findings and recommendations when
implementation is out of scope.

### Phase 1: Root Cause Investigation

**BEFORE attempting ANY fix:**

1. **Read Error Messages Carefully**
   - Don't skip past errors or warnings
   - They often contain the exact solution
   - Read stack traces completely
   - Note line numbers, file paths, error codes

2. **Reproduce Consistently**
   - Can you trigger it reliably?
   - What are the exact steps?
   - Does it happen every time?
   - If not reproducible -> gather more data, don't guess

3. **Check Recent Changes**
   - What changed that could cause this?
   - Git diff, recent commits
   - New dependencies, config changes
   - Environmental differences

4. **Gather Evidence in Multi-Component Systems**

   **WHEN a system has multiple components (CI -> build -> signing, API -> service -> database) and existing evidence does not locate the failure, add targeted diagnostics:**
   ```
   For EACH component boundary:
     - Log what data enters component
     - Log what data exits component
     - Verify environment/config propagation
     - Check state at each layer

   Run once to gather evidence showing WHERE it breaks
   THEN analyze evidence to identify failing component
   THEN investigate that specific component
   ```

   For example, compare a request's identifier, input shape, and result at the
   API, worker, and database boundaries to locate where behavior diverges. Record
   redacted state or presence, never secret values or broad environment dumps.

5. **Trace Data Flow**

   **WHEN error is deep in call stack:**

   See [root-cause-tracing.md](root-cause-tracing.md) in this directory for the complete backward tracing technique.

   **Quick version:**
   - Where does bad value originate?
   - What called this with bad value?
   - Keep tracing up until you find the source
   - Fix at source, not at symptom

For recurring failures, unclear causal links, or an explicit Five Whys request,
optionally use the `five-whys` skill. Follow the evidence across multiple
causal paths when needed; do not force a question chain for a clear local bug.

### Phase 2: Pattern Analysis

**Find the pattern before fixing:**

1. **Find Working Examples**
   - Locate similar working code in same codebase
   - What works that's similar to what's broken?

2. **Compare Against References**
   - Read the relevant reference implementation and version-specific contracts
   - Understand the dependencies and assumptions before applying the pattern

3. **Identify Differences**
   - Compare working and failing cases. Prioritize differences that could explain
     the observed failure, including small differences.
   - Test those explanations and broaden the investigation when the evidence
     does not support them.

4. **Understand Dependencies**
   - What other components does this need?
   - What settings, config, environment?
   - What assumptions does it make?

### Phase 3: Hypothesis and Testing

**Scientific method:**

1. **Form Single Hypothesis**
   - State clearly: "I think X is the root cause because Y"
   - Write it down
   - Be specific, not vague

2. **Test Minimally**
   - Make the SMALLEST possible change to test hypothesis
   - One variable at a time
   - Don't fix multiple things at once

3. **Verify Before Continuing**
   - Did it work? Yes -> Phase 4
   - Didn't work? Form NEW hypothesis
   - DON'T add more fixes on top

4. **When You Don't Know**
   - Say "I don't understand X"
   - Don't pretend to know
   - Ask for help
   - Research more

### Phase 4: Implementation

1. Create a focused reproduction or regression check for meaningful behavior or
   security changes. Confirm that it demonstrates the original failure. For
   low-impact changes, use appropriate existing checks or a manual reproduction.
2. Fix the identified cause with a focused change. Avoid unrelated refactoring or
   stacking several speculative fixes together.
3. Verify the original failure and related behavior with
   `verification-before-completion`, then remove temporary diagnostics.
4. If the fix fails, return to the evidence and reassess the hypothesis. Repeated
   failures may reveal shared state, coupling, or a flawed assumption. Discuss
   material design changes with the user; do not infer architectural failure
   solely from an arbitrary attempt count.

## When the cause is external or remains uncertain

Environmental and timing-dependent failures still have causes. Separate a
confirmed external cause from a hypothesis that remains unverified. State what
you reproduced, what the evidence supports, and which observations are missing;
do not declare the investigation complete merely because a failure is intermittent.

When more evidence is unavailable, report the limit and the next useful check.
Within the authorized task, consider mitigation such as a timeout, clearer error,
or bounded retry. Before retrying, check whether the operation is safe to repeat;
an ambiguous failure after a side effect can otherwise duplicate work or data.

## Supporting Techniques

These techniques are part of systematic debugging and available in this directory:

- **[root-cause-tracing.md](root-cause-tracing.md)** - Trace bugs backward through call stack to find original trigger
- **[defense-in-depth.md](defense-in-depth.md)** - Add validation at multiple layers after finding root cause
- **[condition-based-waiting.md](condition-based-waiting.md)** - Replace arbitrary timeouts with condition polling

**Related skills:**
- **`five-whys`** - Optional evidence-backed causal questioning for recurring or unclear failures
- **`verification-before-completion`** - Verify fix worked before claiming success
