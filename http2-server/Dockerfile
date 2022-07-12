ARG BUILDER_WORKSPACE="/workspace"
FROM golang:1.18-alpine AS builder

ARG BUILDER_WORKSPACE
WORKDIR ${BUILDER_WORKSPACE}

COPY . .

RUN go install


RUN go build -o program main.go

FROM alpine:3

ARG BUILDER_WORKSPACE

COPY --from=builder ${BUILDER_WORKSPACE}/program ./

EXPOSE 9092

CMD ./program