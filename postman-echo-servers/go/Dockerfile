ARG BUILDER_WORKSPACE="/workspace"
FROM golang:1.18-alpine AS builder

ARG BUILDER_WORKSPACE
WORKDIR ${BUILDER_WORKSPACE}

ADD service.go service.go
ADD go.mod go.mod

RUN go build -o program service.go

FROM alpine:3

ARG BUILDER_WORKSPACE

COPY --from=builder ${BUILDER_WORKSPACE}/program ./

EXPOSE 9092

CMD ./program