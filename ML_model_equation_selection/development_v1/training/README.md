# Training

Native Kira reductions provide equation-membership labels for six physical profiles. All target batches from a profile stay in training. The records retain targets, the master basis, exact coefficient comparisons, equation features, seed/operator identifiers and selected-support labels.

A label of one means that the equation's nonzero integral support appears in the final regenerated native system. Equations with the same support can share a label. This is a conservative supervision proxy; it does not prove necessity or a minimum equation set. Symmetry and preferred-basis relations remain under native control.

Run s04_experiment.py collect, then s06_train.py on a scheduled compute node. The model uses a probability tree of depth at most eight and twenty-four features. The split is by physical profile, not by equation.
