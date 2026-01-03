# Build stage
FROM golang:1.21-alpine AS builder

WORKDIR /app

# Copy go mod files
COPY go/go.mod ./
# Note: go.sum might not exist yet, so we don't copy it specifically to avoid errors
# if it exists, it will be caught by the copy below if we change the strategy.

# Copy source
COPY go/main.go ./

# Build the binary
RUN go build -o rdw-server main.go

# Final stage
FROM alpine:latest

# Install ca-certificates for HTTPS requests to RDW API
RUN apk --no-cache add ca-certificates

WORKDIR /root/

# Copy the binary from builder
COPY --from=builder /app/rdw-server .

# Run the server
ENTRYPOINT ["./rdw-server"]
