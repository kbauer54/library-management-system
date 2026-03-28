# Public Library Management System
# create_tables.sql
# Run with: mysql -u root -p < create_tables.sql

CREATE DATABASE IF NOT EXISTS library_db;
USE library_db;

-- Drop tables in reverse FK order to avoid constraint errors
DROP TABLE IF EXISTS EventRegistrations;
DROP TABLE IF EXISTS Events;
DROP TABLE IF EXISTS Fines;
DROP TABLE IF EXISTS Reservations;
DROP TABLE IF EXISTS Loans;
DROP TABLE IF EXISTS Inventory;
DROP TABLE IF EXISTS Staff;
DROP TABLE IF EXISTS Patrons;
DROP TABLE IF EXISTS BookAuthors;
DROP TABLE IF EXISTS Books;
DROP TABLE IF EXISTS Authors;
DROP TABLE IF EXISTS Publishers;
DROP TABLE IF EXISTS Genres;
DROP TABLE IF EXISTS Branches;

# CATALOG CLUSTER

CREATE TABLE Genres (
    genre_id    INT PRIMARY KEY,
    genre_name  VARCHAR(100) NOT NULL
);

CREATE TABLE Publishers (
    publisher_id    INT PRIMARY KEY,
    publisher_name  VARCHAR(100) NOT NULL
);

CREATE TABLE Authors (
    author_id   INT PRIMARY KEY,
    name        VARCHAR(150) NOT NULL
);

CREATE TABLE Books (
    book_id             INT PRIMARY KEY,
    title               VARCHAR(255) NOT NULL,
    isbn                VARCHAR(20),
    publication_year    YEAR,
    genre_id            INT,
    publisher_id        INT,
    FOREIGN KEY (genre_id)      REFERENCES Genres(genre_id),
    FOREIGN KEY (publisher_id)  REFERENCES Publishers(publisher_id)
);

CREATE TABLE BookAuthors (
    book_id     INT,
    author_id   INT,
    PRIMARY KEY (book_id, author_id),
    FOREIGN KEY (book_id)   REFERENCES Books(book_id),
    FOREIGN KEY (author_id) REFERENCES Authors(author_id)
);

# BRANCH & INVENTORY CLUSTER

CREATE TABLE Branches (
    branch_id   INT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    address     VARCHAR(255),
    hours       VARCHAR(255)
);

CREATE TABLE Staff (
    staff_id        INT PRIMARY KEY,
    name            VARCHAR(150) NOT NULL,
    email           VARCHAR(150) UNIQUE,
    password_hash   VARCHAR(255),
    role            ENUM('librarian', 'admin', 'clerk') NOT NULL,
    branch_id       INT,
    FOREIGN KEY (branch_id) REFERENCES Branches(branch_id)
);

CREATE TABLE Patrons (
    patron_id       INT PRIMARY KEY,
    name            VARCHAR(150) NOT NULL,
    email           VARCHAR(150) UNIQUE,
    password_hash   VARCHAR(255),
    membership_date DATE,
    home_branch_id  INT,
    FOREIGN KEY (home_branch_id) REFERENCES Branches(branch_id)
);

CREATE TABLE Inventory (
    inventory_id        INT PRIMARY KEY,
    book_id             INT,
    branch_id           INT,
    copies_available    INT DEFAULT 0,
    copies_total        INT DEFAULT 0,
    FOREIGN KEY (book_id)   REFERENCES Books(book_id),
    FOREIGN KEY (branch_id) REFERENCES Branches(branch_id)
);

# CIRCULATION CLUSTER

CREATE TABLE Loans (
    loan_id         INT PRIMARY KEY,
    inventory_id    INT,
    patron_id       INT,
    checkout_date   DATE NOT NULL,
    due_date        DATE NOT NULL,
    return_date     DATE,
    status          ENUM('active', 'returned', 'returned_late') NOT NULL,
    FOREIGN KEY (inventory_id)  REFERENCES Inventory(inventory_id),
    FOREIGN KEY (patron_id)     REFERENCES Patrons(patron_id)
);

CREATE TABLE Reservations (
    reservation_id      INT PRIMARY KEY,
    book_id             INT,
    patron_id           INT,
    reservation_date    DATE NOT NULL,
    status              ENUM('waiting', 'ready', 'fulfilled') NOT NULL,
    FOREIGN KEY (book_id)   REFERENCES Books(book_id),
    FOREIGN KEY (patron_id) REFERENCES Patrons(patron_id)
);

CREATE TABLE Fines (
    fine_id     INT PRIMARY KEY,
    patron_id   INT,
    loan_id     INT,
    amount      DECIMAL(6,2) NOT NULL,
    paid_status ENUM('paid', 'unpaid') NOT NULL,
    FOREIGN KEY (patron_id) REFERENCES Patrons(patron_id),
    FOREIGN KEY (loan_id)   REFERENCES Loans(loan_id)
);

# EVENTS CLUSTER

CREATE TABLE Events (
    event_id    INT PRIMARY KEY,
    name        VARCHAR(150) NOT NULL,
    description TEXT,
    event_date  DATE NOT NULL,
    branch_id   INT,
    staff_id    INT,
    capacity    INT,
    FOREIGN KEY (branch_id) REFERENCES Branches(branch_id),
    FOREIGN KEY (staff_id)  REFERENCES Staff(staff_id)
);

CREATE TABLE EventRegistrations (
    patron_id           INT,
    event_id            INT,
    registration_date   DATE NOT NULL,
    PRIMARY KEY (patron_id, event_id),
    FOREIGN KEY (patron_id) REFERENCES Patrons(patron_id),
    FOREIGN KEY (event_id)  REFERENCES Events(event_id)
);