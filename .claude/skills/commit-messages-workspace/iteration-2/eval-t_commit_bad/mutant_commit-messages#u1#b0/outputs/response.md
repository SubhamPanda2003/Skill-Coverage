Fix cache eviction off-by-one comparison

The eviction check used <= instead of <, causing
entries to be evicted one cycle too early. Changed
the comparison operator to < so entries are only
evicted once they actually exceed the threshold.