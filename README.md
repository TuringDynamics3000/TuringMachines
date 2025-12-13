# TuringResolve™
## Authoritative Outcomes for Regulated Financial Actions

TuringResolve is the **authoritative system of record for outcomes** in regulated financial workflows.

It determines **whether an action may proceed**, **under which policy**, **with what evidence**, and **who is accountable** — and records that determination as an immutable event.

TuringResolve is not a platform of tools.  
It is a **resolve authority**.

All services in this repository exist to **inform, constrain, explain, or enforce a resolve**.  
The resolve itself is final, explicit, auditable, and replayable.

---

## Resolve Authority Principle

In regulated systems, **signals are not resolves**.

Risk scores, biometric matches, AML checks, and policy rules are **inputs**.

A resolve is only made when TuringResolve emits a:

**decision.finalised**

That event is the **sole source of truth**.

Kafka is the resolve ledger.  
Databases are projections.  
Enforcement is downstream.

---

## Canonical Output: decision.finalised

The authoritative output of the system is the **decision.finalised event**  
(see docs/decision-authority/decision_finalised.schema.json).

Everything else in the system exists to produce, explain, enforce, or audit this event.

---

## Resolve Lifecycle

Signals collected  
→ Risk & policy evaluated  
→ Resolve finalised (event emitted)  
→ Enforcement / review / audit

Only **decision.finalised** events represent authoritative outcomes.

---

## Components (Product View)

- **TuringCapture™** – Evidence generation  
- **TuringOrchestrate™** – Workflow & step-up logic  
- **TuringRiskBrain™** – Risk intelligence (inputs, not authority)  
- **TuringPolicy™** – Jurisdiction policy runtime  
- **TuringSettleGuard™** – Downstream enforcement  
- **TuringResolve™** – Human override & review  
- **TuringCore™ (Optional)** – Ledger projection only

TuringResolve does **not** require a core banking system.

---

## Event Sourcing

Kafka topics are the **system of record**:
- events are immutable
- state is derived via projections
- resolves are replayable and auditable

---

## Final Principle

**Signals inform.  
Policies constrain.  
TuringResolve decides.  
Events remember.**
