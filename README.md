# LebiNova demos: five small systems for the same kind of work

These are standalone demos that mirror the problems LebiNova's lead and client operations face: triaging leads, confirming appointments, reporting on sales, answering questions from documents, and running agents safely. Each one is a few hundred lines of standard-library Python with its own tests. None of them calls a live service: the SMS sender, the LLM, and the data are all stubs, so they run offline.

They are not client work and not production deployments. The production system they draw on is the [LebiNova platform](../readmes/LebiNova-README.md), which contains the Lead Operator agent and the Founder OS admin.

| Demo | What it shows | Run tests |
|---|---|---|
| [lead_triage](lead_triage/) | Rules handle clear cases, an LLM handles the rest, out-of-range LLM answers fall back to human review, and the pipeline is scored against a labeled set (accuracy and LLM share). | `cd lead_triage && python3 -m unittest` |
| [sms_confirm_bot](sms_confirm_bot/) | Appointment reminders with quiet hours, reply classification (cancel overrides confirm), and escalation of anything it cannot classify. | `cd sms_confirm_bot && python3 -m unittest` |
| [sql_report_kit](sql_report_kit/) | Date-bucketed sales totals in SQL, a covering index, and a test that checks the query plan actually uses it. | `cd sql_report_kit && python3 -m unittest` |
| [rag_doc_qa](rag_doc_qa/) | Retrieval over markdown with section-level citations, a stopword filter, "no answer" when nothing matches, and recall@k on labeled questions. | `cd rag_doc_qa && python3 -m unittest` |
| [agent_escalation_worker](agent_escalation_worker/) | Bounded agent steps: low-risk actions run, risky actions wait for approval, errors and missing evidence become escalations, and everything is written to an audit log. | `cd agent_escalation_worker && python3 -m unittest` |

## Design rules across all five

- **Fail loudly.** An error, an invalid model answer, or missing evidence is recorded as an escalation, never as success.
- **Measure what the model decides.** Each demo has a test or evaluation that checks its outputs against expected results.
- **Stub the outside world.** Senders, models, and data are injected, so swapping in Twilio, OpenAI, or a real database changes one argument.

## Requirements

Python 3.10 or newer. No third-party packages.
