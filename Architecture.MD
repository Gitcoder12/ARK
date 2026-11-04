# ARK ARCHITECTURE.MD - System Blueprint

## 0. OVERVIEW
ARK is not a monolithic AI. It is a defensive pipeline designed to evaluate, stress-test, and constrain autonomous agents. This document outlines the data flow and structural layers of the framework.

## 1. THE EXECUTION PIPELINE
Every action an agent attempts to take must traverse the following pipeline. There are no shortcuts.

```text
[ Agent ] 
   ↓ (Proposes Action)
[ ARK Evaluation Layer (SafetyMonitor) ]
   ├── Goal Integrity Check
   ├── Reward Integrity Check
   ├── Memory Integrity Check
   ├── Policy / Constraint Checks
   └── Risk Assessment
   ↓ 
[ ALLOW / BLOCK / REPLAN ]
   ↓ (If ALLOW)
[ Warden (Internal Blocker) ] -> Checks for prompt injection and rogue logic.
   ↓
[ Crucible (External Blocker) ] -> Redacts secrets, blocks malicious payloads.
   ↓
[ ARK Chip (Hardware Interlock) ] -> Hardware gate. Cuts power if Adharma detected.
   ↓
[ Environment / Robotics Actuators ]
   ↓
[ Metrics + Traces (painter/) ]
