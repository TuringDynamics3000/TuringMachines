# TuringDecision™
## Decision Authority for Regulated Financial Actions

TuringDecision is the **authoritative system of record for decisions** in regulated financial workflows.

It determines **whether an action may proceed**, **under which policy**, **with what evidence**, and **who is accountable** — and records that determination as an immutable event.

TuringDecision is not a platform of tools.  
It is a **decision authority**.

All services in this repository exist to **inform, constrain, explain, or enforce a decision**.  
The decision itself is final, explicit, auditable, and replayable.

---

## Decision Authority Principle

In regulated systems, **signals are not decisions**.

Risk scores, biometric matches, AML checks, and policy rules are **inputs**.

A decision is only made when TuringDecision emits a:

**decision.finalised**

That event is the **sole source of truth**.

Kafka is the decision ledger.  
Databases are projections.  
Enforcement is downstream.

---

## Canonical Output: decision.finalised

The authoritative output of the system is the **DecisionFinalised event**  
(see docs/decision-authority/decision_finalised.schema.json).

Everything else in the system exists to produce, explain, enforce, or audit this event.

---

## Decision Lifecycle

Signals collected  
→ Risk & policy evaluated  
→ Decision finalised (event emitted)  
→ Enforcement / review / audit

Only **decision.finalised** events represent authoritative outcomes.

---

## Components (Product View)

- **TuringCapture™** – Evidence generation  
- **TuringOrchestrate™** – Workflow & step-up logic  
- **TuringRiskBrain™** – Risk intelligence (inputs, not authority)  
- **TuringPolicy™** – Jurisdiction policy runtime  
- **TuringSettleGuard™** – Downstream enforcement  
- **TuringInvestigator™** – Human override & review  
- **TuringCore™ (Optional)** – Ledger projection only

TuringDecision does **not** require a core banking system.

---

## Event Sourcing

Kafka topics are the **system of record**:
- events are immutable
- state is derived via projections
- decisions are replayable and auditable

---

## Final Principle

**Signals inform.  
Policies constrain.  
TuringDecision decides.  
Events remember.**
