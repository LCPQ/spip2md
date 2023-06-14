# Use an old version to test compatibility
FROM python:3.7

WORKDIR /usr/src/app

RUN pip install poetry
COPY pyproject.toml README.md LICENSE ./
COPY spip2md/ spip2md.yml ./
RUN poetry shell
RUN poetry install

CMD [ "poetry shell" ]
CMD [ "spip2md" ]
