# First development attempt

This attempt used cached packed Kira weights as equation-support identifiers. Its very low label matching rate triggered an identifier audit. Validation was stopped before the reserved test. All completed records, code and fitted weights remain here. The next attempt uses explicit integral indices, updates labels across regeneration and rechecks matching. No speedup is claimed from this attempt.

The subsequent audit found an uninitialized coefficient accumulator in label construction. These labels and this fitted candidate are invalid and remain excluded from the final model and its scientific results. Exact reduction outputs still passed because Kira supplied native fallback.
