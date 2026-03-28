import requests
import csv
import time

# ---------------------------
# This script is used to pull data on books from the Open Library API
# Some data cleaning is done through the process and the output is 5 different csv files
# books.csv, authors.csv, book_authors.csv, publishers.csv, and genres.csv
# ---------------------------


# ---------------------------
# CONFIGURATION
# ---------------------------

SUBJECTS = ["fiction", "mystery", "science_fiction", "history", "biography"]
LIMIT_PER_SUBJECT = 60   # 5 subjects × 60 = 300 books
OUTPUT_DIR = "./"   # Sets the output of the data to the same folder as this script
# ---------------------------

books = {}
authors = {}
publishers = {}
genres = {}
book_authors = []

book_counter = 1
author_counter = 1
publisher_counter = 1
genre_counter = 1

author_name_to_id = {}
publisher_name_to_id = {}
genre_name_to_id = {}

# ---------------------------
# HELPER FUNCTIONS
# ---------------------------

def clean(value):
    # Strip leading/trailing whitespace and quotes from a string
    if not value:
        return ""
    # Strip start and ending whitespaces, then double quotes, then single quotes, then whitespaces again
    return str(value).strip().strip('"').strip("'").strip()

def write_csv(filename, rows, fieldnames):
    path = OUTPUT_DIR + filename

    with open(path, "w", newline="", encoding="utf-8") as f: # w opens the file in write mode, newline argument prevents Python from placing extra line endings
        # Create a csv writer object
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="|", quoting=csv.QUOTE_NONE, escapechar="\\")
        writer.writeheader() # Writes the column names as the first row of the file
        writer.writerows(rows) # Writes all the data rows at once
        # Row output should look like:
        # 1|The Old Man and the Sea|9780684801223|1952|1|4
    print(f"    {filename} - {len(rows)} rows")

# ---------------------------
# MAIN FETCH LOOP
# ---------------------------

print("Starting Open Library fetch...\n")

for subject in SUBJECTS:
    print(f"  Fetching subject: {subject}")
    url = (
        f"https://openlibrary.org/search.json"
        f"?subject={subject}"
        f"&limit={LIMIT_PER_SUBJECT}"
        f"&fields=key,title,isbn,first_publish_year,author_name,publisher,subject"
    )

    try:
        # Make an HTTP request to the Open Library API URL, like visiting the browser, but in code
        response = requests.get(url, timeout=15)
        # Catch errors where the URL is not found
        response.raise_for_status()
        # Turns the response into a Python dictionary so we can work with it
        data = response.json()
    except Exception as e:
        print(f"  ERROR fetching {subject}: {e}")
        continue

    # Pull the list of books out of the response dictionary
    docs = data.get("docs", [])
    print(f"  Got {len(docs)} results")

    # --- Genre ----------
    # Replace _ with whitespace in genre titles
    genre_label = subject.replace("_", " ").title()
    # If we have not come across the genre yet, add it to our genre dictionary
    if genre_label not in genre_name_to_id:
        genre_name_to_id[genre_label] = genre_counter
        genres[genre_counter] = {
            "genre_id": genre_counter,
            "genre_name": genre_label
        }
        genre_counter += 1
    # Record the genre_id for use later
    gid = genre_name_to_id[genre_label]

    # For each book in the collection of books returned
    for doc in docs:

        # --- Title ----------
        title = clean(doc.get("title", ""))
        if not title:
            continue

        # Skip duplicate titles (some titles are in multiple subjects)
        existing_titles = {b["title"] for b in books.values()}
        if title in existing_titles:
            continue

        # --- ISBN ----------
        isbns = doc.get("isbn", [])
        isbn = clean(isbns[0]) if isbns else ""

        # --- Year ----------
        year = doc.get("first_publish_year", "")

        # --- Publisher ----------
        pub_list = doc.get("publisher", [])
        # Clean the publisher name, limit it to 100 characters, if nothing is in pub_list, then return "Unknown Publisher"
        pub_name = clean(pub_list[0])[:100] if pub_list else "Unknown Publisher"

        # If we come across a new publisher, add it to the publisher dictionary
        if pub_name not in publisher_name_to_id:
            publisher_name_to_id[pub_name] = publisher_counter
            publishers[publisher_counter] = {
                "publisher_id": publisher_counter,
                "publisher_name": pub_name
            }
            publisher_counter += 1
        pid = publisher_name_to_id[pub_name]

        # --- Book ----------
        bid = book_counter
        books[bid] = {
            "book_id": bid,
            "title": title,
            "isbn": isbn,
            "publication_year": year if year else "",
            "genre_id": gid,
            "publisher_id": pid
        }
        book_counter += 1

        # --- Authors ----------
        author_names = doc.get("author_name", [])

        for aname in author_names[:3]:
            aname = clean(aname)
            if not aname:
                continue

            if aname not in author_name_to_id:
                author_name_to_id[aname] = author_counter
                authors[author_counter] = {
                    "author_id": author_counter,
                    "name": aname
                }
                author_counter += 1

            aid = author_name_to_id[aname]
            book_authors.append({"book_id": bid, "author_id": aid})

    time.sleep(0.5)  # Pause for each subject to avoid overloading the server

# ---------------------------
# WRITE CSVs
# ---------------------------

print("\nWriting CSVs...")

# Use the write_csv function made above to create a csv for each category pertaining to the books
write_csv("books.csv",
    list(books.values()),
    ["book_id", "title", "isbn", "publication_year", "genre_id", "publisher_id"])

write_csv("authors.csv",
    list(authors.values()),
    ["author_id", "name"])

write_csv("book_authors.csv",
    book_authors,
    ["book_id", "author_id"])

write_csv("publishers.csv",
    list(publishers.values()),
    ["publisher_id", "publisher_name"])

write_csv("genres.csv",
    list(genres.values()),
    ["genre_id", "genre_name"])

# Print the results
print(f"""
------------------------------------
Done! Summary:
  Books:        {len(books)}
  Authors:      {len(authors)}
  BookAuthors:  {len(book_authors)}
  Publishers:   {len(publishers)}
  Genres:       {len(genres)}
------------------------------------
""")
