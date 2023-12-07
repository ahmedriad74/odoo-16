FROM ubuntu
RUN apt-get update && apt-get install -y ca-certificates curl && apt-get clean && rm -rf /var/lib/apt/lists
COPY . .
ENTRYPOINT ["bash", "./backup.sh"]