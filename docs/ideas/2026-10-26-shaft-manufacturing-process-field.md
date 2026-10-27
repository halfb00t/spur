# A manufacturing-process field that selects the shaft root factor h_fP

Date: 2026-10-26
Source: Phase 31 plan 31-05 checkpoint, divergence D1: DIN 5480-1 cl. 6 Table 3 and cl. 7.1 make h_fP depend on the process (broaching, hobbing, mill-broaching, cold rolling).
Related files:
- src/spur/din5480.py:30 (H_FP)
- src/spur/shaft_calc.py (hobbed_root_warning)

## Context
`root_d` is the theoretical (broaching) root, and a warning gives the hobbed value. A process field
(broach / hob / mill-broach / ...) would pick h_fP and print the root for the part the user will make.

## Why it matters
The printed root would match the user's process without a warning to read and subtract.

## Next step
Needs a new Lxx decision first (a new user parameter, L05 and L03 apply). Its default must be the
current broaching root so every existing part and link stays unchanged. Revisit when a user asks for a
hobbed or mill-broached shaft.
