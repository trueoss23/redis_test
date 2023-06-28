FROM python

RUN pip install fastapi uvicorn redis


COPY . .

ENV REDIS_HOST=redis
ENV REDIS_PORT=6379

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
