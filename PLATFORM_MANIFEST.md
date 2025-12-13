# TuringMachines Platform Manifest

This repository is a **platform monorepo**.

## Purpose
Provide governed, auditable decision engines for regulated environments.

## Structure
- /platform   → core engines and shared logic
- /products   → commercial product wrappers
- /shared     → internal libraries

## Maturity Labels
- GA
- Beta
- Experimental

## Ownership Rule
No product may embed logic that belongs in the platform layer.
