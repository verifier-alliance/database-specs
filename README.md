# database-specs

This repository contains the schema used for the Verifier Alliance database. The full schema is contained in `./database.sql`. This file is a generated dump from all applied schema migrations. The initial database schema can be found in `./migrations/20250717103432_database.sql`. It includes documentation about the schema and its tables.
For a graphical representation of the schema, you can visit the [VerA docs](https://verifieralliance.org/docs/database-schema).

## Migrations

For keeping track of schema changes, we use a lightweight tool called [dbmate](https://github.com/amacneil/dbmate). Please follow the instructions on its GitHub repository for installation.

### Prerequisites

As a prerequisite for using dbmate, you should have a `.env` file configured with the database connection details.
For this, copy the `.env.template` file to `.env` and replace the database connection string.

### Running migrations

For running all pending migrations against the database configured in `.env`, you can simply run:

```bash
dbmate migrate
```

### Adding a new migration

Any migration added should be capable of updating the live VerA production and test database.
This means that a migration should also transform data if necessary.

For setting up a new migration, please use a fresh database, because dbmate will dump the current state of the database into `database.sql` after running the migration.
For using a fresh database, simply configure an unused database name in the `.env` file.

The process for adding a new migration is as follows:

1. Create a new migration file: `dbmate new <migration_name>`
2. Add the SQL needed for the schema change in the generated migration file (e.g., `migrations/20250717103432_add_new_table.sql`)
   - The migration file should also include a `down` section to revert the changes if necessary.
   - It should transform any data if necessary, e.g., for filling a new column with default values or copying data from one table to another.
   - Ideally, the migration file should be idempotent, meaning it can be run multiple times without causing errors.
3. Create a fresh database with the name configured in `.env`: `dbmate create`
4. Run the migrations on the new database in order to generate the `database.sql` dump: `dbmate migrate`
5. You can drop the database again: `dbmate drop`
6. Both the migration file and the updated `database.sql` should be committed to the repository.

Finally, any changes to the schema should be reflected in the `tests/`.
Please update the tests if necessary, or add new tests to cover the changes made in the schema.
