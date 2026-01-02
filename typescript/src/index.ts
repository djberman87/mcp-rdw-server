/**
 * RDW Vehicle Info MCP Server (TypeScript)
 * Authors: Dirk-Jan Berman & Gemini 3
 * License: MIT
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import fetch from "node-fetch";

const server = new Server(
  {
    name: "rdw-server-ts",
    version: "1.2.2",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

const RDW_API_ENDPOINT = "https://opendata.rdw.nl/resource/m9d7-ebf2.json";
const RDW_AXLES_API_ENDPOINT = "https://opendata.rdw.nl/resource/3huj-srit.json";

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "get_vehicle_info",
        description: "Haal gedetailleerde technische informatie op over een Nederlands voertuig op basis van het kenteken.",
        inputSchema: {
          type: "object",
          properties: {
            kenteken: {
              type: "string",
              description: "Het kenteken van het voertuig (bijv. '41TDK8', '41-TDK-8'). Tekens worden automatisch genormaliseerd.",
            },
          },
          required: ["kenteken"],
        },
      },
      {
        name: "get_vehicle_axles",
        description: "Haal informatie op over de assen van een voertuig op basis van het kenteken.",
        inputSchema: {
          type: "object",
          properties: {
            kenteken: {
              type: "string",
              description: "Het kenteken van het voertuig (bijv. '41TDK8'). Tekens worden automatisch genormaliseerd.",
            },
          },
          required: ["kenteken"],
        },
      },
    ],
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name } = request.params;
  const args = request.params.arguments as { kenteken: string };
  const kenteken = args.kenteken.toUpperCase().replace(/[-\s]/g, "");

  if (name === "get_vehicle_info") {
    try {
      const response = await fetch(`${RDW_API_ENDPOINT}?kenteken=${kenteken}`);
      if (!response.ok) {
        throw new Error(`RDW API error: ${response.status} ${response.statusText}`);
      }
      
      const data = (await response.json()) as any[];
      
      if (data.length === 0) {
        return {
          content: [
            {
              type: "text",
              text: `Geen voertuig gevonden voor kenteken: ${kenteken}`,
            },
          ],
        };
      }
      
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(data[0], null, 2),
          },
        ],
      };
    } catch (error: any) {
      return {
        content: [
          {
            type: "text",
            text: `Fout bij het ophalen van voertuiggegevens: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }

  if (name === "get_vehicle_axles") {
    try {
      const response = await fetch(`${RDW_AXLES_API_ENDPOINT}?kenteken=${kenteken}`);
      if (!response.ok) {
        throw new Error(`RDW API error: ${response.status} ${response.statusText}`);
      }
      
      const data = (await response.json()) as any[];
      
      if (data.length === 0) {
        return {
          content: [
            {
              type: "text",
              text: `Geen as-informatie gevonden voor kenteken: ${kenteken}. Let op: lichte personenauto's hebben vaak geen vermelding in deze dataset.`,
            },
          ],
        };
      }
      
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(data, null, 2),
          },
        ],
      };
    } catch (error: any) {
      return {
        content: [
          {
            type: "text",
            text: `Fout bij het ophalen van as-informatie: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
  
  throw new Error("Tool niet gevonden");
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("RDW MCP server (TypeScript) running on stdio");
}

main().catch((error) => {
  console.error("Fatal error in main():", error);
  process.exit(1);
});
