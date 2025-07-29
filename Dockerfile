FROM python:3.12-alpine AS builder

ARG PIP_INDEX_URL=https://pypi.org/simple/

WORKDIR /app

RUN pip install -U pip -i $PIP_INDEX_URL
RUN pip install pdm

COPY pyproject.toml pdm.lock ./

RUN pdm export --without-hashes --prod -f requirements -o requirements.txt
RUN pip install -r requirements.txt -i $PIP_INDEX_URL

FROM python:3.12-alpine

WORKDIR /app


COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY pyproject.toml pdm.lock ./
COPY src/ebnr ./ebnr
COPY config.toml ./

ENV EBNR_CONCURRENCY_RESOLVE_PLAYLIST=10
ENV EBNR_BASE_URL=http://0.0.0.0:8000
EXPOSE 8000

CMD ["python", "-m", "ebnr"]
