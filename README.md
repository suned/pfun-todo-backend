# pfun-todo-backend
This is an example repository showcasing how to use [pfun](http://pfun.rtfd.io) with an [ASGI]()
server by implementing the [Todo Backend](). We're using [FastAPI]() here, 
but any ASGI server would do. [Postgres]() is used for persistence through `pfun.sql`.

## Running
Requires [Docker]():
```console
$ docker-compose up
```

Use the OpenAPI docs at the `/docs` endpoint for a description of the endpoints.
