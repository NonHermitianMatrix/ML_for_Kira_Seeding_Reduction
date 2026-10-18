# Integration

s06_build_sector_storage.py creates sector_storage.patch and sector_weights.patch, plus the exact build recipe. These patches bound sector arrays, retain the order of admitted sectors, and count trivial sectors without an exhaustive scan. s07_sector_checks.py compares it with native allocation. The compiled executable stays under .tools/kira-sector-storage. The patch retains native allocation unless KIRA_BOUNDED_SECTOR_ARRAYS and the existing sector restriction are active.

Read the main folder guide for execution order and limits.
