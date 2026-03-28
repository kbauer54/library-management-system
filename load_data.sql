# Public Library Management System
# load_data.sql

USE library_db;

-- Setting the folder path to where each of the CSV files are stored
SET @data_path = '/Users/kolbebauer/Desktop/CS485-term-project/term-project-code/';

-- Each CSV file is delimited with pipes, and skipping one row to skip the header row of each file

-- Load parent tables first

-- 1. Genres
LOAD DATA LOCAL INFILE '/Users/kolbebauer/Desktop/CS485-term-project/term-project-code/genres.csv'
INTO TABLE Genres
FIELDS TERMINATED BY '|'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(genre_id, genre_name);

-- 2. Publishers
LOAD DATA LOCAL INFILE '/Users/kolbebauer/Desktop/CS485-term-project/term-project-code/publishers.csv'
INTO TABLE Publishers
FIELDS TERMINATED BY '|'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(publisher_id, publisher_name);

-- 3. Authors
LOAD DATA LOCAL INFILE '/Users/kolbebauer/Desktop/CS485-term-project/term-project-code/authors.csv'
INTO TABLE Authors
FIELDS TERMINATED BY '|'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(author_id, name);

-- 4. Books
LOAD DATA LOCAL INFILE '/Users/kolbebauer/Desktop/CS485-term-project/term-project-code/books.csv'
INTO TABLE Books
FIELDS TERMINATED BY '|'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(book_id, title, isbn, publication_year, genre_id, publisher_id);

-- 5. BookAuthors
LOAD DATA LOCAL INFILE '/Users/kolbebauer/Desktop/CS485-term-project/term-project-code/book_authors.csv'
INTO TABLE BookAuthors
FIELDS TERMINATED BY '|'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(book_id, author_id);

-- 6. Branches
LOAD DATA LOCAL INFILE '/Users/kolbebauer/Desktop/CS485-term-project/term-project-code/branches.csv'
INTO TABLE Branches
FIELDS TERMINATED BY '|'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(branch_id, name, address, hours);

-- 7. Staff
LOAD DATA LOCAL INFILE '/Users/kolbebauer/Desktop/CS485-term-project/term-project-code/staff.csv'
INTO TABLE Staff
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(staff_id, name, email, password_hash, role, branch_id);

-- 8. Patrons
LOAD DATA LOCAL INFILE '/Users/kolbebauer/Desktop/CS485-term-project/term-project-code/patrons.csv'
INTO TABLE Patrons
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(patron_id, name, email, password_hash, membership_date, home_branch_id);

-- 9. Inventory
LOAD DATA LOCAL INFILE '/Users/kolbebauer/Desktop/CS485-term-project/term-project-code/inventory.csv'
INTO TABLE Inventory
FIELDS TERMINATED BY '|'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(inventory_id, book_id, branch_id, copies_available, copies_total);

-- 10. Loans
LOAD DATA LOCAL INFILE '/Users/kolbebauer/Desktop/CS485-term-project/term-project-code/loans.csv'
INTO TABLE Loans
FIELDS TERMINATED BY '|'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(loan_id, inventory_id, patron_id, checkout_date, due_date, return_date, status);

-- 11. Reservations
LOAD DATA LOCAL INFILE '/Users/kolbebauer/Desktop/CS485-term-project/term-project-code/reservations.csv'
INTO TABLE Reservations
FIELDS TERMINATED BY '|'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(reservation_id, book_id, patron_id, reservation_date, status);

-- 12. Fines
LOAD DATA LOCAL INFILE '/Users/kolbebauer/Desktop/CS485-term-project/term-project-code/fines.csv'
INTO TABLE Fines
FIELDS TERMINATED BY '|'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(fine_id, patron_id, loan_id, amount, paid_status);

-- 13. Events
LOAD DATA LOCAL INFILE '/Users/kolbebauer/Desktop/CS485-term-project/term-project-code/events.csv'
INTO TABLE Events
FIELDS TERMINATED BY '|'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(event_id, name, description, event_date, branch_id, staff_id, capacity);

-- 14. EventRegistrations
LOAD DATA LOCAL INFILE '/Users/kolbebauer/Desktop/CS485-term-project/term-project-code/event_registrations.csv'
INTO TABLE EventRegistrations
FIELDS TERMINATED BY '|'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(patron_id, event_id, registration_date);

-- VERIFY ROW COUNTS

SELECT 'Genres'             AS table_name, COUNT(*) AS row_count FROM Genres
UNION ALL
SELECT 'Publishers',         COUNT(*) FROM Publishers
UNION ALL
SELECT 'Authors',            COUNT(*) FROM Authors
UNION ALL
SELECT 'Books',              COUNT(*) FROM Books
UNION ALL
SELECT 'BookAuthors',        COUNT(*) FROM BookAuthors
UNION ALL
SELECT 'Branches',           COUNT(*) FROM Branches
UNION ALL
SELECT 'Staff',              COUNT(*) FROM Staff
UNION ALL
SELECT 'Patrons',            COUNT(*) FROM Patrons
UNION ALL
SELECT 'Inventory',          COUNT(*) FROM Inventory
UNION ALL
SELECT 'Loans',              COUNT(*) FROM Loans
UNION ALL
SELECT 'Reservations',       COUNT(*) FROM Reservations
UNION ALL
SELECT 'Fines',              COUNT(*) FROM Fines
UNION ALL
SELECT 'Events',             COUNT(*) FROM Events
UNION ALL
SELECT 'EventRegistrations', COUNT(*) FROM EventRegistrations;
