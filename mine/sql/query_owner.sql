WITH
    database AS (
        SELECT
            datdba::regrole::TEXT AS owner,
            'database' AS object,
            datname AS name
        FROM pg_database
        WHERE
            datname !~ 'late'
    ),
    schema AS (
        SELECT
            nspowner::regrole::TEXT AS owner,
            'schema' AS object,
            nspname AS name
        FROM pg_namespace
        WHERE
            nspname !~ '_'
    ),
    class AS (
        SELECT
            relowner::regrole::TEXT AS owner,
            concat(
                relnamespace::regnamespace::TEXT,
                '_',
                relkind
            ) AS object,
            relname AS name
        FROM pg_class
        WHERE
            relnamespace::regnamespace::TEXT !~ '_'
    ),
    proc AS (
        SELECT
            proowner::regrole::TEXT AS owner,
            concat(
                pronamespace::regnamespace::TEXT,
                '_',
                'proc'
            ) AS object,
            proname AS name
        FROM pg_proc
        WHERE
            pronamespace::regnamespace::TEXT !~ '_'
    ),
    result as (
        SELECT *
        FROM database
        UNION ALL
        SELECT *
        FROM schema
        UNION ALL
        SELECT *
        FROM class
        UNION ALL
        SELECT *
        FROM proc
    )
SELECT *
FROM result
WHERE
    owner !~ '_'
ORDER BY owner, object, name