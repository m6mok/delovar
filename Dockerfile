FROM python:3.10

WORKDIR /app

ENV VIRTUAL_ENV=/home/packages/.venv
ADD https://astral.sh/uv/install.sh /install.sh
RUN chmod -R 655 /install.sh && /install.sh && rm /install.sh

COPY ./requirements.txt .
RUN /root/.cargo/bin/uv venv /home/packages/.venv
RUN /root/.cargo/bin/uv pip install --no-cache -r requirements.txt

ENV PATH="/home/packages/.venv/bin:$PATH"

COPY . /app/

EXPOSE 8000
