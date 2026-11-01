# Five Whys: optional causal questioning

Use this technique when explicitly requested, when a problem recurs, or when
causal links remain unclear. It applies to software failures, churn, delays, and
process problems. A routine bug with an evidenced local cause does not need a
question chain or a formal incident report.

Respect the requested scope. For analysis-only work, inspect permitted evidence
and recommend next steps without changing files, adding instrumentation,
implementing solutions, or performing other mutations. A suggested experiment
or fix is a recommendation, not permission to execute it.

## Follow the evidence

1. Define the observed problem concretely: what happened, when, and how it differs
   from the expected outcome. Use measurements when available.
2. Ask what caused that observation. For each proposed link, record the evidence
   supporting it and distinguish facts from hypotheses. A plausible explanation
   alone does not establish causation.
3. Follow supported answers with further questions. Use fewer or more than five;
   the name is not a quota. Branch when evidence suggests multiple contributing
   causes, and keep competing explanations distinct. Testing one hypothesis at a
   time does not mean assuming there is only one causal path.
4. Stop a path when the cause is adequately supported for the task, or when the
   available evidence runs out. Identify unknowns and the next evidence needed
   rather than filling gaps with assumptions. Do not force every local defect
   into an organizational or process failure.
5. Propose corrections for the supported causes and a proportionate way to check
   their effect. Separate immediate symptom relief from recurrence prevention;
   either may be useful. Execute changes only within the authorized task.

Focus on conditions, decisions, and systems rather than personal blame. During
conversation, ask a focused question at a time when an answer is needed; reuse
existing evidence instead of making the user repeat it. Softer questions such as
“What was happening at the time?” or “What were you trying to accomplish?” can
help uncover context without turning the investigation into an interrogation.

## Example: delayed delivery

Suppose delivery records show two contributing paths:

- Work waited for approval; timestamps show the designated approver was absent
  and no alternate was assigned.
- A separate shipment arrived late; carrier tracking confirms the delay, but
  its cause is unknown.

The first path supports considering backup approval coverage. The second needs
more evidence before recommending a supplier or shipping-process change. Neither
path needs exactly five questions, and the example does not prove what caused
any real delay.

## Report proportionately

Summarize the observed problem, supported causal paths and their evidence,
unresolved hypotheses, and recommended next steps with an appropriate validation
method. A short explanation is often enough. Dates, participant lists, audit
artifacts, and a fixed report template are optional when the task calls for them.
