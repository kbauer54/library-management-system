import csv
import random
import re
from datetime import datetime, timedelta

# ---------------------------
# CONFIGURATION
# ---------------------------
PATRON_COUNT = 75
STAFF_COUNT  = 20
BRANCH_COUNT = 5
OUTPUT_DIR   = "./"
# ---------------------------


# ---------------------------
# HELPER FUNCTIONS
# ---------------------------

def clean(value):
    # Strip whitespaces, then double quotes, then single quotes, then whitespaces again
    if not value:
        return ""
    return str(value).strip().strip('"').strip("'").strip()

def strip_html(value):
    # Remove HTML tags like <p>, <strong>, <figure> from descriptions
    if not value:
        return ""
    return re.sub(r"<[^>]+>", "", value).strip()

def parse_date(value):
    """
    Extract a clean YYYY-MM-DD date from various formats.
    Seattle uses: 2023-04-15T00:00:00
    Chicago uses: 2026-04-08T14:00:00
    """
    if not value:
        return ""
    # Strip everything after T (the time part)
    date_part = value.split("T")[0].strip()
    try:
        dt = datetime.strptime(date_part, "%Y-%m-%d")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return ""

def make_due_date(checkout_date_str, days=14):
    # Calculate a due date 14 days after checkout
    try:
        dt = datetime.strptime(checkout_date_str, "%Y-%m-%d")
        due = dt + timedelta(days=days)
        return due.strftime("%Y-%m-%d")
    except ValueError:
        return ""

def make_return_date(due_date_str):
    """
    Randomly decide if a book was returned:
    - 70% returned on time (0-14 days before due)
    - 20% returned late (1-14 days after due)
    - 10% not yet returned (NULL)
    """
    if not due_date_str:
        return ""
    roll = random.random()
    if roll < 0.10:
        return ""  # not returned yet
    try:
        due = datetime.strptime(due_date_str, "%Y-%m-%d")
        if roll < 0.80:
            # returned on time — random day between checkout and due date
            offset = random.randint(-14, 0)
        else:
            # returned late
            offset = random.randint(1, 14)
        return_dt = due + timedelta(days=offset)
        return return_dt.strftime("%Y-%m-%d")
    except ValueError:
        return ""

# The following function is similar to the one in the open library fetch script
def write_csv(filename, rows, fieldnames):
    path = OUTPUT_DIR + filename
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="|", quoting=csv.QUOTE_NONE, escapechar="\\")
        writer.writeheader()
        writer.writerows(rows)
    print(f"    {filename} — {len(rows)} rows")

# ---------------------------
# LOAD EXISTING BOOK IDS from books.csv
# So we can link loans to real books
# ---------------------------

book_ids = []
try:
    with open("books.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="|")
        for row in reader:
            book_ids.append(int(row["book_id"]))
    print(f"  Loaded {len(book_ids)} book IDs from books.csv")
except FileNotFoundError:
    print("  WARNING: books.csv not found — loans will use random book IDs 1-300")
    book_ids = list(range(1, 301))

# ---------------------------
# CLEAN SEATTLE CHECKOUTS
# and convert to loans.csv
# ---------------------------

print("\nCleaning Seattle checkouts to loans.csv")

loans = []
loan_id = 1

with open("checkouts_raw.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)  # comma delimited (Seattle default)
    for row in reader:

        checkout_date = parse_date(clean(row.get("checkoutdatetime", "")))
        if not checkout_date:
            continue

        due_date    = make_due_date(checkout_date)
        return_date = make_return_date(due_date)

        # Determine loan status
        if not return_date:
            status = "active"
        elif return_date > due_date:
            status = "returned_late"
        else:
            status = "returned"

        # Randomly assign to a real book and patron
        book_id   = random.choice(book_ids)
        patron_id = random.randint(1, PATRON_COUNT)

        # inventory_id = book_id * branch combos (book_id * 10 + branch_id)
        # Simple formula: each book has copies at each branch
        branch_id    = random.randint(1, BRANCH_COUNT)
        inventory_id = (book_id - 1) * BRANCH_COUNT + branch_id

        loans.append({
            "loan_id":       loan_id,
            "inventory_id":  inventory_id,
            "patron_id":     patron_id,
            "checkout_date": checkout_date,
            "due_date":      due_date,
            "return_date":   return_date,
            "status":        status
        })
        loan_id += 1

write_csv("loans.csv", loans,
    ["loan_id", "inventory_id", "patron_id", "checkout_date", "due_date", "return_date", "status"])

# ---------------------------
# DERIVE FINES from late loans
# ---------------------------

print("Deriving fines → fines.csv")

fines = []
fine_id = 1
FINE_RATE = 0.50  # $0.50 per day

for loan in loans:
    if loan["status"] == "returned_late" and loan["return_date"] and loan["due_date"]:
        try:
            due    = datetime.strptime(loan["due_date"], "%Y-%m-%d")
            ret    = datetime.strptime(loan["return_date"], "%Y-%m-%d")
            days_late = (ret - due).days
            if days_late > 0:
                amount     = round(days_late * FINE_RATE, 2)
                paid_status = random.choice(["paid", "paid", "unpaid"])  # 2/3 chance paid
                fines.append({
                    "fine_id":     fine_id,
                    "patron_id":   loan["patron_id"],
                    "loan_id":     loan["loan_id"],
                    "amount":      amount,
                    "paid_status": paid_status
                })
                fine_id += 1
        except ValueError:
            continue

write_csv("fines.csv", fines,
    ["fine_id", "patron_id", "loan_id", "amount", "paid_status"])

# ─────────────────────────────────────────
# CLEAN CHICAGO EVENTS → events.csv
# ─────────────────────────────────────────

print("Cleaning Chicago events → events.csv")

events = []
event_id_counter = 1

with open("events_raw.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)  # comma delimited (Chicago default)
    for row in reader:

        name = clean(row.get("title", ""))
        if not name:
            continue

        description = strip_html(clean(row.get("description", "")))
        event_date  = parse_date(clean(row.get("start", "")))
        if not event_date:
            continue

        # Randomly assign to one of your 5 branches and a staff member
        branch_id = random.randint(1, BRANCH_COUNT)
        staff_id  = random.randint(1, STAFF_COUNT)
        capacity  = random.randint(10, 50)

        events.append({
            "event_id":    event_id_counter,
            "name":        name[:150],         # match VARCHAR(150) in your schema
            "description": description[:500],  # trim long descriptions
            "event_date":  event_date,
            "branch_id":   branch_id,
            "staff_id":    staff_id,
            "capacity":    capacity
        })
        event_id_counter += 1

write_csv("events.csv", events,
    ["event_id", "name", "description", "event_date", "branch_id", "staff_id", "capacity"])

# ─────────────────────────────────────────
# DERIVE RESERVATIONS
# Pick patron/book combos and set status
# ─────────────────────────────────────────

print("Deriving reservations → reservations.csv")

reservations = []
seen_pairs = set()
reservation_id = 1

while len(reservations) < 50:
    patron_id = random.randint(1, PATRON_COUNT)
    book_id   = random.choice(book_ids)
    pair      = (patron_id, book_id)

    if pair in seen_pairs:
        continue
    seen_pairs.add(pair)

    # Random reservation date in 2023-2024
    start = datetime(2023, 1, 1)
    offset = random.randint(0, 730)
    res_date = (start + timedelta(days=offset)).strftime("%Y-%m-%d")
    status = random.choice(["waiting", "waiting", "ready", "fulfilled"])

    reservations.append({
        "reservation_id":   reservation_id,
        "book_id":          book_id,
        "patron_id":        patron_id,
        "reservation_date": res_date,
        "status":           status
    })
    reservation_id += 1

write_csv("reservations.csv", reservations,
    ["reservation_id", "book_id", "patron_id", "reservation_date", "status"])

# ─────────────────────────────────────────
# DERIVE EVENT REGISTRATIONS
# Randomly assign 2-3 patrons per event
# ─────────────────────────────────────────

print("Deriving event registrations → event_registrations.csv")

event_registrations = []
seen_pairs = set()

for event in events:
    num_registrants = random.randint(2, 3)
    assigned = 0
    attempts = 0
    while assigned < num_registrants and attempts < 20:
        patron_id = random.randint(1, PATRON_COUNT)
        pair = (patron_id, event["event_id"])
        attempts += 1
        if pair in seen_pairs:
            continue
        seen_pairs.add(pair)

        # Registration date is before the event date
        try:
            event_dt = datetime.strptime(event["event_date"], "%Y-%m-%d")
            offset   = random.randint(1, 30)
            reg_date = (event_dt - timedelta(days=offset)).strftime("%Y-%m-%d")
        except ValueError:
            reg_date = event["event_date"]

        event_registrations.append({
            "patron_id":         patron_id,
            "event_id":          event["event_id"],
            "registration_date": reg_date
        })
        assigned += 1

write_csv("event_registrations.csv", event_registrations,
    ["patron_id", "event_id", "registration_date"])

# ─────────────────────────────────────────
# DERIVE INVENTORY
# Each book gets 1-3 copies at each branch
# ─────────────────────────────────────────

print("Deriving inventory → inventory.csv")

inventory = []
inventory_id = 1

for book_id in book_ids:
    for branch_id in range(1, BRANCH_COUNT + 1):
        copies_total     = random.randint(1, 3)
        copies_available = random.randint(0, copies_total)
        inventory.append({
            "inventory_id":      inventory_id,
            "book_id":           book_id,
            "branch_id":         branch_id,
            "copies_available":  copies_available,
            "copies_total":      copies_total
        })
        inventory_id += 1

write_csv("inventory.csv", inventory,
    ["inventory_id", "book_id", "branch_id", "copies_available", "copies_total"])

# ---------------------------
# SUMMARY
# ---------------------------

print(f"""
─────────────────────────────────────
All files cleaned! Here is the output:

  loans.csv                ({len(loans)} rows)
  fines.csv                ({len(fines)} rows)
  events.csv               ({len(events)} rows)
  reservations.csv         ({len(reservations)} rows)
  event_registrations.csv  ({len(event_registrations)} rows)
  inventory.csv            ({len(inventory)} rows)
─────────────────────────────────────
""")
