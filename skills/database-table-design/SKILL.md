---
name: database-table-design
description: Apply 9 fundamental rules and best practices when designing relational database schemas and MySQL tables. Use when designing databases, drafting DDL statements, creating table schemas, reviewing database architecture, or optimizing table structures.
---

# Database Table Design

A comprehensive guide for agents to design robust, efficient, and scalable relational database tables (specifically MySQL and similar RDBMS) adhering to 9 core principles.

## When to Use

Use this skill whenever:

- Designing new database tables or schemas.
- Drafting DDL (`CREATE TABLE`, `ALTER TABLE`) statements.
- Reviewing or auditing existing relational table architectures.
- Advising on database normalization, indexing strategies, or data types.

## Core Rules and Guidelines

### 1. Include Mandatory Audit Columns

Every table must include standard tracking columns for traceability and concurrency control:

- `version`: Tracks modification count; essential for optimistic and pessimistic locking.
- `creator_id` (or `created_by`): Identifier of the user or process creating the record.
- `modify_by` (or `updated_by`): Identifier of the user or process performing the last update.
- `create_time` (or `created_at`): Timestamp when the record was created.
- `update_time` (or `updated_at`): Timestamp when the record was last modified.

### 2. Document Every Column with Comments

Never leave columns without semantic context in DDL:

- Add `COMMENT` clauses to all column definitions in DDL.
- For enumerated or status fields (`TINYINT`), explicitly document each discrete value (e.g. `COMMENT '1: active, 2: deleted, 3: pending'`).

### 3. Implement Soft Deletes

Avoid physical hard deletion (`DELETE FROM`) to preserve audit trails:

- Standard approach: Use `is_deleted` (`TINYINT`, default 0) and `deleted_at` (`DATETIME`/`TIMESTAMP`).
- Single-column approach: Use `deleted_at` defaulting to `NULL`, populated with the timestamp when deleted.
- Note: Be mindful of indexing behavior when querying nullable `deleted_at` fields in massive datasets.

### 4. Use Table-Specific Prefixes for Column Names

Prevent naming collisions and ambiguity during multi-table `JOIN` operations:

- Prefix column names with the entity name or a clear abbreviation (e.g. `feed_id`, `feed_title`, `acc_number`).
- Avoid generic column names like `id`, `name`, `status`, or `created_at` across multiple joined tables without table scoping.

### 5. Vertically Partition Wide Tables (> 20 Columns)

Avoid bloated rows that waste buffer pool memory and increase I/O cost:

- Threshold: If a table exceeds 20 columns, split it into primary and detail tables.
- Primary Table: High-frequency query columns, list/search views (e.g. `id`, `title`, `thumbnail`, `status`, `create_time`).
- Detail Table: Large, infrequently accessed fields (e.g. `content`, `full_description`), linked via a 1-to-1 relationship.

### 6. Select Precise Data Types and Lengths

Optimize memory and disk footprint:

- Strings: Do not default to `VARCHAR(255)`. Use the realistic maximum (e.g. `VARCHAR(100)` for titles, `VARCHAR(2)` for ISO language codes).
- Integers: Use `TINYINT` (1 byte, range 0-255) for status flags and category IDs instead of `INT` (4 bytes). Reserve `BIGINT` (8 bytes) for primary keys of very large tables.

### 7. Enforce NOT NULL with Sensible Defaults

Avoid unconstrained `NULL` values:

- `NULL` complicates business logic, consumes extra overhead, and degrades index optimization in MySQL.
- Define columns as `NOT NULL`. Provide explicit default values (`DEFAULT ''`, `DEFAULT 0`) where a value is not immediately known.

### 8. Design Targeted Indexing Strategies

Index based on selectivity and access patterns:

- Prefix index names with `idx_` (or `uniq_` for unique indexes).
- High Cardinality: Focus indexes on fields with high dispersion (e.g. user IDs, compound index on `(creator_id, create_time)`).
- Low Cardinality Pitfall: Avoid single-column indexes on low-cardinality fields like `status` where 90%+ records share the same value (optimizer falls back to full table scans).
- Mitigation: Combine status with high-cardinality fields in composite indexes, use partitioning, or leverage application-level caching.

### 9. Adhere to 3NF and Consider Pragmatic Denormalization

Ensure data integrity while balancing performance:

- Third Normal Form (3NF): Ensure every non-key attribute depends only on the primary key, eliminating transitive dependencies.
- Scalability: Where read performance is paramount at massive scale, selectively denormalize or advance to higher normal forms (4NF, 5NF) with strict synchronization mechanisms.

## Gotchas

- Do not create single-column indexes on boolean or small-range status flags; combine them with selective filters like timestamps or IDs.
- Do not blindly use `SELECT *` on wide tables; adhere to the vertical partitioning model.
- Always verify that all status values are documented in the table comment before deploying DDL.


## Mandatory Global Rules & Tools
- **Rules Compliance:** You MUST strictly obey any system-wide or domain-specific rules defined in the 
ules/ directory, if it exists.


## Mandatory Global Rules & MCPs
- **Rules Compliance:** You MUST strictly obey any system-wide or domain-specific rules defined in the 
ules/ directory, if it exists.
- **MCP Usage:** For any technical task, planning, design, code reviewing, testing, or skill cloning, you MUST ALWAYS use the context7 and sequentialthinking MCP tools. Do not bypass them.
