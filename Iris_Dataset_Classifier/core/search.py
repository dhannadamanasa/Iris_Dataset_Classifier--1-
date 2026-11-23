def search_records(records, keyword="", species="All"):
    keyword = (keyword or "").strip().lower()
    found = []
    for record in records:
        if species != "All" and record.get("species") != species:
            continue
        haystack = " ".join(str(v) for v in record.values()).lower()
        if keyword and keyword not in haystack:
            continue
        found.append(record)
    return found
