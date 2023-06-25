

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


def create_counts(assignee_id):
    r.hset(assignee_id, 'count_tasks', 0)
    r.hset(assignee_id, 'count_comments_tasks', 0)
    r.hset(assignee_id, 'count_observers', 0)


def increment_count(name_dict: str, count_name: str, num: int):
    print('incterment', name_dict)
    r.hincrby(name_dict, count_name, num)


def get_all_counts(assignee_id):
    count_tasks = r.hget(assignee_id, 'count_tasks')
    count_comments_tasks = r.hget(assignee_id, 'count_comments_tasks')
    count_observers = r.hget(assignee_id, 'count_observers')
    print(count_tasks, count_comments_tasks, count_observers)
    return {'count_tasks': count_tasks,
            'count_comments_tasks': count_comments_tasks,
            'count_observers': count_observers}


@app.post('/assignee/')
def create_assignee(assignee: Assignee):
    # some code
    create_counts(assignee.id_)


@app.post('/task/')
def create_task(task: Task):
    # some code
    if r.exists(task.assignee.id_):
        increment_count(task.assignee.id_, 'count_tasks', 1)
        increment_count(task.obderver.id_, 'count_observers', 1)


@app.patch('/task/task_id/')
def update_comments():
    pass


@app.put('/task/task_id/')
def update_task(task: Task):
    # some code
    if r.exists(task.assignee):
        increment_count(task.assignee, 'count_observers', 1)


@app.get('/assignee/assignee_id')
def get_counts(assignee_id):
    print(r.keys('*'))
    return get_all_counts(assignee_id)


if __name__ == '__main__':
    uvicorn.run('main:app', host='localhost', port=8002, reload=True)
