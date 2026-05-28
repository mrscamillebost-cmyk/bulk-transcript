def safe_notes(text):
    return str(text).replace(",", ";").replace("\n", " ").strip()
