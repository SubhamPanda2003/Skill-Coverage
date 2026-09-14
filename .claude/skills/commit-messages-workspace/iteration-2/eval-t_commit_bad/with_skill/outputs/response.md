Fix cache eviction off-by-one

The eviction check used <= instead of <, causing
entries to be evicted one cycle before they should
have expired. Change the comparison to < so entries
are evicted only once they truly exceed their TTL.