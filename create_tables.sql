CREATE TABLE todos (
    id serial PRIMARY KEY,
    title text,
    "order" int,
    completed BOOLEAN
)
