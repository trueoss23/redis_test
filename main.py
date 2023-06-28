

from fastapi import FastAPI, Depends, HTTPException
from config import get_settings
from pydantic import BaseSettings

import uvicorn
import redis


class Assignee(BaseSettings):
    id_: int
    name: str


class Task(BaseSettings):
    comments: str
    assignee: Assignee
    obderver: Assignee


settings = get_settings()
r = redis.Redis()
app = FastAPI(title=settings.app_name)


def create_counts(assignee):
    r.hset(assignee.name, 'count_tasks', 0)
    r.hset(assignee.name, 'count_comments_tasks', 0)
    r.hset(assignee.name, 'count_observers', 0)
    r.hset(assignee.name, 'id_', assignee.id_)


def increment_count(name_dict: str, count_name: str, num: int):
    print('incterment', name_dict)
    r.hincrby(name_dict, count_name, num)


def get_all_counts(name):
    print(name, r.keys(name))
    if r.keys(name):
        id_ = r.hget(name, 'id_')
        count_tasks = r.hget(name, 'count_tasks')
        count_comments_tasks = r.hget(name, 'count_comments_tasks')
        count_observers = r.hget(name, 'count_observers')
        # print(count_tasks, count_comments_tasks, count_observers)
        return {'name': name,
                'id_': id_,
                'count_tasks': count_tasks,
                'count_comments_tasks': count_comments_tasks,
                'count_observers': count_observers}
    else:
        raise HTTPException(status_code=404, detail=f'Not found{name}')


def add_names_in_db_memory(name: str):
    r.sadd('names_assignee', name)


def add_count_comments(comment: str):
    names = r.smembers('names_assignee')
    for name in names:
        check_name = f'@{name.decode()}'
        if check_name in comment:
            increment_count(name, 'count_comments_tasks', 1)


@app.post('/assignee/')
def create_assignee(assignee: Assignee):
    # some code
    add_names_in_db_memory(assignee.name)
    create_counts(assignee)


@app.post('/task/')
def create_task(task: Task):
    # some code
    if r.exists(task.assignee.name):
        increment_count(task.assignee.name, 'count_tasks', 1)
        increment_count(task.obderver.name, 'count_observers', 1)
    add_count_comments(task.comments)


@app.patch('/task/task_id/')
def update_comments(comment: str):
    add_count_comments(comment)


@app.put('/task/task_id/')
def update_task(task: Task):
    # some code
    if r.exists(task.assignee.name):
        increment_count(task.assignee.name, 'count_observers', 1)


@app.get('/assignee/assignee_id')
def get_counts(name):
    print(r.keys('*'))
    return get_all_counts(name)


if __name__ == '__main__':
    uvicorn.run('main:app', host='localhost', port=8002, reload=True)
