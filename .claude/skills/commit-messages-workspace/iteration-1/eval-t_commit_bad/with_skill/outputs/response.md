Fix off-by-one in cache eviction check

Change eviction comparison from `<=` to `<` so entries
are no longer evicted one cycle early.