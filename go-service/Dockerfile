FROM golang:1.26-alpine as builder

WORKDIR /app

COPY go.mod ./
COPY main.go ./

RUN go build -o server main.go

FROM debian:bookworm-slim

RUN useradd -m app

WORKDIR /app

COPY --from=builder /app/server .

RUN chown app:app /app/server .

USER app

EXPOSE 8081

CMD [ "./server" ]