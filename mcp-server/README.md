# mindwave-journeys-mcp

A TypeScript MCP server for the mindwave-journeys project. Communicates over stdio.

## Setup

```bash
cd mcp-server
npm install
npm run build
```

## Run

```bash
npm start
```

## Develop

```bash
npm run dev      # tsc --watch
npm run inspector  # launch MCP Inspector against the built server
```

## Tools

- `echo` — returns the input `message` back as text. Starter example; replace with project-specific tools.

## Wire into Claude Code

Add to `~/.claude.json` or your project `.mcp.json`:

```json
{
  "mcpServers": {
    "mindwave-journeys": {
      "command": "node",
      "args": ["/absolute/path/to/mindwave-journeys/mcp-server/dist/index.js"]
    }
  }
}
```
