## 2026-07-03 - [Django Related Manager Query Overhead]
**Learning:** Using `values_list()` or other QuerySet methods on a related manager (even if prefetched) triggers a new database query. This causes N+1 problems when iterating over a list of objects and trying to extract IDs from their related fields.
**Action:** Use list comprehensions or set comprehensions on the prefetched manager (e.g., `{p.pk for p in offer.products.all()}`) to leverage in-memory data instead of hitting the database again.
