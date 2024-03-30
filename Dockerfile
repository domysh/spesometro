FROM --platform=$BUILDPLATFORM oven/bun:1 as frontend
ENV NODE_ENV=production
WORKDIR /build
COPY package.json bun.lockb /build/
RUN bun install
COPY ./frontend/ .
RUN bun run build


#Building main conteiner
FROM --platform=$TARGETARCH python as base

WORKDIR /execute
ADD ./backend/requirements.txt /execute/requirements.txt
RUN pip3 install --no-cache-dir --break-system-packages -r /execute/requirements.txt --no-warn-script-location
COPY ./backend/ /execute/
COPY --from=frontend /app/dist/ ./frontend/

CMD ["python3", "/execute/app.py"]