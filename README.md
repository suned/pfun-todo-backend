# pfun-todo-backend
This is an example repository showcasing how to use [pfun](http://pfun.rtfd.io) with an [ASGI](https://asgi.readthedocs.io/en/latest/)
server by implementing the [Todo Backend](https://todobackend.com/). We're using [FastAPI](https://fastapi.tiangolo.com/) here, 
but any ASGI server would do. [Postgres](https://www.postgresql.org/) is used for persistence through `pfun.sql`.

## Running
Requires [Docker](https://www.docker.com/):
```console
$ docker-compose up
```

Use the OpenAPI docs at the `/docs` endpoint for a description of the endpoints.
