const { Server } = require("@modelcontextprotocol/sdk/server/index.js");
const { StdioServerTransport } = require("@modelcontextprotocol/sdk/server/stdio.js");
const { CallToolRequestSchema, ListToolsRequestSchema } = require("@modelcontextprotocol/sdk/types.js");
const fetch = (...args) => import('node-fetch').then(({default: fetch}) => fetch(...args));

const server = new Server(
  {
    name: "rdw-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

const RDW_API_ENDPOINT = "https://opendata.rdw.nl/resource/m9d7-ebf2.json";

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "get_vehicle_info",
        description: "Haal informatie op over een voertuig op basis van het kenteken (RDW Open Data).",
        inputSchema: {
          type: "object",
          properties: {
            kenteken: {
              type: "string",
              description: "Het kenteken van het voertuig (bijv. 41TDK8 of 41-TDK-8). Tekens worden automatisch omgezet naar hoofdletters en streepjes worden verwijderd.",
            },
          },
          required: ["kenteken"],
        },
      },
    ],
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "get_vehicle_info") {
    const kenteken = request.params.arguments.kenteken.toUpperCase().replace(/-/g, "");
    
    try {
      const response = await fetch(`${RDW_API_ENDPOINT}?kenteken=${kenteken}`);
      if (!response.ok) {
        throw new Error(`RDW API error: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      if (data.length === 0) {
        return {
          content: [
            {
              type: "text",
              text: `Geen voertuig gevonden met kenteken: ${kenteken}`,
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
    } catch (error) {
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
  
  throw new Error("Tool niet gevonden");
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("RDW MCP server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error in main():", error);
  process.exit(1);
});
