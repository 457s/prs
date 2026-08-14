SELECT
    relnamespace::regnamespace::TEXT AS SCHEMA,
    relkind,
    relname
FROM pg_class
WHERE
    relnamespace::regnamespace::TEXT ~ 'temp';