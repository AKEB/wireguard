FROM lscr.io/linuxserver/wireguard:latest

COPY --from=golang:1.13-alpine /usr/local/go/ /usr/local/go/
COPY --from=james/wg-api:latest /bin/wg-api /bin/wg-api
ENV PATH="/usr/local/go/bin:${PATH}"

# RUN go install github.com/jamescun/wg-api
