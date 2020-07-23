from __future__ import annotations

from typing import Any, Optional, Union

from fastapi import FastAPI
from pydantic import BaseModel
from asyncpg import PostgresError
from typing_extensions import Protocol

from pfun import Try, Effect, List, get_environment, sql, Dict, catch, success, error


class Todo(BaseModel):
    id: Optional[int] = None
    order: int
    title: str
    completed: bool = False

    class Config:
        allow_mutation = False


Todos = List[Todo]


def as_todo(row: Dict[str, Any]) -> Try[TypeError, Todo]:
    return catch(TypeError)(lambda: Todo(**row))


def handle_no_results(
    reason: Union[TypeError, PostgresError, sql.EmptyResultSetError]
) -> Try[Union[PostgresError, TypeError], None]:
    if isinstance(reason, sql.EmptyResultSetError):
        return success(None)
    return error(reason)


class Model:
    def get_todos(self
                  ) -> Effect[sql.HasSQL, 
                              Union[TypeError, PostgresError], 
                              Todos]:
        return sql.fetch('select * from todos').and_then(
            sql.as_type(Todo)
        )

    def get_todo(self, todo_id: int
                 ) -> Effect[sql.HasSQL, 
                             Union[PostgresError, TypeError], 
                             Optional[Todo]]:
        return sql.fetch_one(
            'select * from todos where id = $1', todo_id
        ).and_then(
            as_todo
        ).recover(
            handle_no_results
        )

    def patch_todo(self, todo: Todo
                   ) -> Effect[sql.HasSQL, PostgresError, Todo]:
        query = '''
            update todos
            set "order" = $1, title = $2, completed = $3
            where id = $4
        '''
        return sql.execute(
            query, todo.order, todo.title, todo.completed, todo.id
        ).discard_and_then(success(todo))

    def add_todo(self, todo: Todo
                 ) -> Effect[sql.HasSQL, PostgresError, Todo]:
        query = '''
            insert into todos
            ("order", title, completed)
            values ($1, $2, $3)
            returning id
        '''
        return sql.fetch_one(
            query, todo.order, todo.title, todo.completed
        ).map(
            lambda row: Todo(
                id=row['id'],
                order=todo.order,
                title=todo.title,
                completed=todo.completed
            )
        )

    def delete_todos(self) -> Effect[sql.HasSQL, PostgresError, None]:
        return sql.execute('delete from todos').discard_and_then(success(None))

    def delete_todo(self, todo_id: int
                    ) -> Effect[sql.HasSQL, PostgresError, None]:
        return sql.execute(
            'delete from todos where id = $1', todo_id
        ).discard_and_then(
            success(None)
        )


class HasModel(Protocol):
    model: Model


class HasModelAndSQL:
    model: Model
    sql: sql.SQL

    def __init__(self):
        self.model = Model()
        self.sql = sql.SQL('postgres://postgres:password@postgres')


app = FastAPI()


@app.get("/")
async def get_todos() -> Todos:
    """
    Get all todos
    """
    effect = get_environment(HasModel).and_then(
        lambda env: env.model.get_todos()
    )
    return await effect(HasModelAndSQL())


@app.post("/")
async def add_todo(todo: Todo) -> Todo:
    """
    Add a todo
    """
    effect = get_environment(HasModel).and_then(
        lambda env: env.model.add_todo(todo)
    )
    return await effect(HasModelAndSQL())


@app.patch("/")
async def patch_todo(todo: Todo) -> Todo:
    """
    Update a todo
    """
    effect = get_environment(HasModel).and_then(
        lambda env: env.model.patch_todo(todo)
    )
    return await effect(HasModelAndSQL())


@app.delete("/")
async def delete_todos() -> None:
    """
    Delete all todos
    """
    effect = get_environment(HasModel).and_then(
        lambda env: env.model.delete_todos()
    )
    return await effect(HasModelAndSQL())


@app.get("/{todo_id}")
async def get_todo(todo_id: int) -> Union[None, Todo]:
    """
    Get a todo
    """
    effect = get_environment(HasModel).and_then(
        lambda env: env.model.get_todo(todo_id)
    )
    return await effect(HasModelAndSQL())


@app.delete("/{todo_id}")
async def delete_todo(todo_id: int) -> None:
    """
    Delete a todo
    """
    effect = get_environment(HasModel).and_then(
        lambda env: env.model.delete_todo(todo_id)
    )
    return await effect(HasModelAndSQL())
