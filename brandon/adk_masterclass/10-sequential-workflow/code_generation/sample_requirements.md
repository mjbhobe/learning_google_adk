# Sample Requirements for Code Generation Pipeline

A collection of sample problems across three complexity tiers for testing the
code generation → code review → code refactoring sequential pipeline.

---

## Simple Problems

### 1. Temperature Converter

Write a Python module that converts between Celsius, Fahrenheit, and Kelvin.
Include functions for all 6 conversion directions and a CLI that accepts a value
and unit.

### 2. Word Frequency Counter

Write a function that takes a string of text and returns a dictionary of word
frequencies, case-insensitive, ignoring punctuation, sorted by most frequent
first.

### 3. Configurable FizzBuzz

Write a FizzBuzz function that is configurable — the caller can pass in any
number of (divisor, label) pairs instead of hardcoding Fizz/Buzz/3/5.

### 4. Stack Using Two Queues

Implement a Stack class using only two queue (`collections.deque`) instances
internally. Support `push`, `pop`, `peek`, and `is_empty`.

### 5. Palindrome Checker

Write a function that checks if a string is a palindrome, ignoring spaces,
punctuation, and case. Include a second function that finds the longest
palindromic substring.

---

## Medium Complexity Problems

### 1. CSV Report Aggregator

Write a Python function that reads a CSV file of sales transactions (date,
product, quantity, price) and produces a summary report: total revenue per
product, top 5 products by revenue, and monthly revenue trend.

### 2. Password Strength Validator

Implement a password strength checker that scores a password (0–100) based on
length, character variety, common patterns, and dictionary words. Return a score
plus actionable feedback messages.

### 3. File Duplicate Finder

Write a script that scans a directory recursively, finds duplicate files (by
content, not name), groups them, and prints a report showing wasted space. Should
handle large files efficiently using a two-pass hashing strategy.

### 4. In-Memory Key-Value Store with Namespaces

Build a key-value store class that supports namespaces (e.g. `store.set('users:123', data)`),
prefix-based listing (`store.list('users:')`), and bulk delete by prefix.

### 5. Markdown Table Parser

Parse a Markdown table string into a list of dictionaries using headers as keys,
handling column alignment markers, extra whitespace, and missing cells gracefully.

---

## Complex Problems

### 1. LRU Cache with TTL

Implement an LRU (Least Recently Used) cache in Python that also supports
TTL (time-to-live) expiry per key. It should be thread-safe and have O(1)
`get`/`put` operations.

### 2. Token Bucket Rate Limiter

Implement a token bucket rate limiter class in Python that supports per-user
rate limits, burst allowances, and is safe for use in a multi-threaded web
server.

### 3. Recursive Descent Expression Parser

Write a recursive descent parser in Python that evaluates arithmetic expressions
with `+`, `-`, `*`, `/`, parentheses, and unary minus. No use of `eval()`.

### 4. Consistent Hashing Ring

Implement a consistent hashing ring for distributing keys across nodes, with
support for virtual nodes and adding/removing nodes without rehashing all keys.

### 5. Async Job Queue with Retries

Build an async task queue in Python using `asyncio` that supports priority
levels, configurable retry with exponential backoff, a dead-letter queue for
permanently failed jobs, and graceful shutdown.