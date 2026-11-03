# guava-mcp: unofficial Guava Health MCP server (streamable HTTP, stateless).
# Tokens live in GUAVA_HOME; mount a volume there. Grants must exist in one place only.
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends openssl && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY pyproject.toml README.md ./
COPY guava_cli ./guava_cli
RUN pip install --no-cache-dir ".[mcp]"
ENV GUAVA_HOME=/data MCP_TRANSPORT=streamable-http MCP_HOST=0.0.0.0 MCP_PORT=3000 MCP_STATELESS=true
VOLUME /data
EXPOSE 3000
CMD ["guava-mcp"]
