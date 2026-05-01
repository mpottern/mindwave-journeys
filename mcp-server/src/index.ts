#!/usr/bin/env node
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({
  name: "mindwave-journeys-mcp",
  version: "0.1.0",
});

server.registerTool(
  "echo",
  {
    title: "Echo",
    description: "Echoes the provided message back to the caller.",
    inputSchema: {
      message: z.string().describe("The message to echo back"),
    },
  },
  async ({ message }) => ({
    content: [{ type: "text", text: message }],
  }),
);

const transport = new StdioServerTransport();
await server.connect(transport);
