# Engineering Disciplines & Field Measurement Taxonomy

> **Document Type:** Engineering Discipline Taxonomy  
> **Governance Status:** Phase 1 Deliverable  
> **Project:** SATYA — Oil India Limited (SIH 2026)  

---

## 1. Executive Summary

Upstream oil and gas projects involve specialized engineering disciplines executing interdependent scope. Each discipline uses distinct technical terminology, units of measure (UOM), physical deliverables, and quality verification workflows.

SATYA uses discipline classification as a key context filter within **Activity Fingerprinting** to prevent cross-discipline matching errors (e.g., matching a civil trenching log to a piping welding activity).

---

## 2. Discipline Taxonomy Matrix

| Discipline | Core Physical Scope | Common Units of Measure (UOM) | Key Field Terminology & Shorthand | Critical Verifying Evidence |
| :--- | :--- | :--- | :--- | :--- |
| **Civil & Earthworks** | ROW clearing, grading, trenching, pad preparation, bund wall. | $\text{Sq.M}$, $\text{Cu.M}$, $\text{Km}$, $\text{Meters}$ | ROW, grading, grubbing, cut & fill, backfilling, compaction, chainage. | Soil compaction test report, survey alignment sheet. |
| **Structural** | Pipe rack erection, shelter fabrication, foundation concreting, rebar. | $\text{MT}$ (Metric Tons), $\text{Cu.M}$, $\text{Nos}$ | Poured, rebar tying, shuttering, alignment, anchor bolts, torqueing. | Concrete cube test certificate, structural alignment report. |
| **Piping & Pipeline** | Pipe stringing, trenching, bending, welding, lowering, tie-ins, hydrotest. | $\text{Meters}$, $\text{Joints}$, $\text{Dia-Inch}$ | Stringing, beveling, root pass, joint welding, NDT, lowering, HDD, tie-in. | NDT (RT/UT) clearance log, Hydrotest chart certificate. |
| **Mechanical Equipment** | Static vessel erection, pumps, compressors, separators, tanks. | $\text{Nos}$, $\text{MT}$, $\text{Percent}$ | Erection, alignment, leveling, nozzle fit-up, internal tray installation. | Equipment alignment sheet, OEM inspection clearance. |
| **Electrical (E&I)** | Cable laying, transformer installation, earthing, motor wiring. | $\text{Meters}$, $\text{Nos}$, $\text{Runs}$ | Cable trench, pulling, glanding, termination, meggering, earthing grid. | Megger test report, insulation resistance certificate. |
| **Instrumentation** | Transmitter installation, impulse piping, control valve setup, DCS integration. | $\text{Nos}$, $\text{Loops}$, $\text{Signals}$ | Loop checking, calibration, impulse tubing, DCS cold loop, hot loop. | Instrument calibration certificate, Loop test sign-off sheet. |
| **QA / QC** | Independent quality testing, NDT inspection, hydrostatic testing. | $\text{Clearance Ratio}$, $\text{NCR Count}$ | Radiography, Ultrasonic test, Hydrotest clearance, Punch list A/B. | Formal TPIA Clearance Certificate, NCR closure form. |
| **HSE & Safety** | Site safety clearance, toolbox talks, permit-to-work (PTW). | `Boolean` / `Permit ID` | PTW issued, gas check clean, safety induction, incident free hours. | Signed Permit-to-Work form, Safety audit log. |

---

## 3. Cross-Discipline Execution Dependencies

Disciplines execute in strict sequential dependency chains dictated by construction physics:

```
[CIVIL]               [PIPING]                [QA / NDT]              [CIVIL BACKFILL]
Trench Excavation --> Pipe Stringing & =====> NDT Clearance ======> Lowering &
(Chainage 12-14)      Welding (Joints 1-40)   Passed (100%)           Trench Backfill
```

### Operational Matching Value
If a field observation reports "Lowering pipe completed", SATYA's Schedule-Aware Engine checks:
1. Is Civil trenching completed for this chainage?
2. Is Piping welding completed for these joints?
3. Has QA passed NDT clearance?

If QA clearance is missing, SATYA flags an **`UnverifiedSequenceConflict`** or reduces the match confidence score.
