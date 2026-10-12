# Broader scattering families

families.json contains two rational profiles of a massless nonplanar two-loop four-point family and two profiles of a one-loop pentagon. Each batch has sixteen targets; d remains symbolic. The nonplanar propagator list follows the massless limit of topo4 in the original Kira paper. All target indices, scalar-product rules and rank checks are explicit.

../references/ contains bases and master expansions. ../model_test/ contains native and frozen-filter timings and exact source inputs. Match records through the case ID. These tests do not change the original integral collection or its training split. The frozen filter needs native fallback on each profile; the current application guard retains native decisions.

Run the numbered workflow in ../README.md. Preserve existing records and the resource limits.
