# The download's file name does not carry the root shape

Date: 2026-10-08
Source: 19-RESEARCH Open Question 6
Related files:
- src/spur/params.py (`GearParams.slug`)
- src/spur/app.py (the `Content-Disposition` filename)
- src/spur/records.py (the record's `slug`)

## Context

`GearParams.slug()` names teeth, module and pressure angle only:
`spur_z{teeth}_m{module}_pa{pressure_angle}`. Since Phase 19 added `root_shape`, a radial
and a trochoid download of the same gear get the same file name, although the two parts
differ at every tooth root. Most other parameters (profile shift, face width, bore, ...)
already share a name the same way; the root shape is the first one whose difference is the
point of asking for it.

## Why it matters

Two different parts with one name on disk: someone who downloads both to compare, or who
re-downloads after switching `root_shape`, overwrites the first or cannot tell the files
apart. The browser appends `(1)`, the CLI's `-o` is the caller's own name, so it bites the
web download first.

## Next step

Revisit when a user reports mixing them up, or when the default flip is planned (see
`2026-09-21-trochoidal-root-fillets.md`). A slug change renames every download, and the
slug is also written into records, so it needs its own decision (`Lxx`) and a look at what
pins the old names, not a drive-by edit.
