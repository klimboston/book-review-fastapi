FROM golang:1.26-alpine as builder

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .

RUN go build -o server .

FROM debian:bookworm-slim

RUN useradd -m app

WORKDIR /app

COPY --from=builder /app/server .

RUN chown app:app /app/server .

USER app

EXPOSE 8081

CMD [ "./server" ]