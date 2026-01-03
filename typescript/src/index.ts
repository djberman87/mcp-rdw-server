/**
 * RDW Vehicle Info MCP Server (TypeScript)
 * Authors: Dirk-Jan Berman & Gemini 3
 * Version: 2.0.0
 * License: MIT
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

const server = new Server(
  {
    name: "rdw-server-ts",
    version: "2.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

const ENDPOINTS = {
  info: "https://opendata.rdw.nl/resource/m9d7-ebf2.json",
  odometer: "https://opendata.rdw.nl/resource/v3i9-dpe8.json",
  fuel: "https://opendata.rdw.nl/resource/8ys7-d773.json",
  axles: "https://opendata.rdw.nl/resource/3huj-srit.json",
  remarks: "https://opendata.rdw.nl/resource/7ug8-2dtt.json",
  subcategory: "https://opendata.rdw.nl/resource/wj78-6f6f.json",
  tracks: "https://opendata.rdw.nl/resource/p693-vshn.json",
  bodywork: "https://opendata.rdw.nl/resource/vezc-m2t6.json",
  bodywork_specific: "https://opendata.rdw.nl/resource/jhie-znh9.json",
  vehicle_class: "https://opendata.rdw.nl/resource/kmfi-hrps.json"
};

const normalizeKenteken = (kenteken: string) => kenteken.toUpperCase().replace(/[-\s]/g, "");

async function fetchRdwData(endpoint: string, kenteken: string): Promise<any[]> {
  const fetch = (await import("node-fetch")).default;
  try {
    const response = await fetch(`${endpoint}?kenteken=${kenteken}`);
    if (!response.ok) return [];
    return (await response.json()) as any[];
  } catch (error) {
    return [];
  }
}

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "get_vehicle_info",
        description: "Haal algemene voertuiggegevens op (Merk, Model, APK, etc.). Dataset: m9d7-ebf2",
        inputSchema: {
          type: "object",
          properties: {
            kenteken: { type: "string", description: "Het Nederlandse kenteken." },
          },
          required: ["kenteken"],
        },
      },
      {
        name: "get_odometer_judgment",
        description: "Decodeert tellerstand-codes naar tekstuele uitleg (logisch/onlogisch). Dataset: v3i9-dpe8",
        inputSchema: {
          type: "object",
          properties: {
            kenteken: { type: "string", description: "Het Nederlandse kenteken." },
          },
          required: ["kenteken"],
        },
      },
      {
        name: "get_vehicle_fuel",
        description: "Brandstofverbruik en emissiegegevens. Dataset: 8ys7-d773",
        inputSchema: {
          type: "object",
          properties: {
            kenteken: { type: "string", description: "Het Nederlandse kenteken." },
          },
          required: ["kenteken"],
        },
      },
      {
        name: "get_vehicle_axles",
        description: "Informatie over de assen van een voertuig (aslasten, aantal assen). Dataset: 3huj-srit",
        inputSchema: {
          type: "object",
          properties: {
            kenteken: { type: "string", description: "Het Nederlandse kenteken." },
          },
          required: ["kenteken"],
        },
      },
      {
        name: "get_vehicle_remarks",
        description: "Bijzonderheden en specifieke registraties (bijv. taxi, ambulance). Dataset: 7ug8-2dtt",
        inputSchema: {
          type: "object",
          properties: {
            kenteken: { type: "string", description: "Het Nederlandse kenteken." },
          },
          required: ["kenteken"],
        },
      },
      {
        name: "get_vehicle_subcategory",
        description: "Specifieke voertuig-subcategorie. Dataset: wj78-6f6f",
        inputSchema: {
          type: "object",
          properties: {
            kenteken: { type: "string", description: "Het Nederlandse kenteken." },
          },
          required: ["kenteken"],
        },
      },
      {
        name: "get_vehicle_tracks",
        description: "Informatie over rupsband-sets. Dataset: p693-vshn",
        inputSchema: {
          type: "object",
          properties: {
            kenteken: { type: "string", description: "Het Nederlandse kenteken." },
          },
          required: ["kenteken"],
        },
      },
      {
        name: "get_vehicle_bodywork",
        description: "Gecombineerde carrosseriegegevens uit meerdere RDW datasets. Datasets: vezc-m2t6, jhie-znh9, kmfi-hrps",
        inputSchema: {
          type: "object",
          properties: {
            kenteken: { type: "string", description: "Het Nederlandse kenteken." },
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
  const kenteken = normalizeKenteken(args.kenteken);

  try {
    if (name === "get_vehicle_bodywork") {
      const [bodywork, specific, vehicleClass] = await Promise.all([
        fetchRdwData(ENDPOINTS.bodywork, kenteken),
        fetchRdwData(ENDPOINTS.bodywork_specific, kenteken),
        fetchRdwData(ENDPOINTS.vehicle_class, kenteken)
      ]);

      const combined = {
        kenteken,
        carrosserie: bodywork,
        carrosserie_specifiek: specific,
        voertuigklasse: vehicleClass
      };

      if (bodywork.length === 0 && specific.length === 0 && vehicleClass.length === 0) {
        return { content: [{ type: "text", text: `Geen carrosseriegegevens gevonden voor kenteken: ${kenteken}` }] };
      }

      return { content: [{ type: "text", text: JSON.stringify(combined, null, 2) }] };
    }

    const endpointMap: Record<string, string> = {
      get_vehicle_info: ENDPOINTS.info,
      get_odometer_judgment: ENDPOINTS.odometer,
      get_vehicle_fuel: ENDPOINTS.fuel,
      get_vehicle_axles: ENDPOINTS.axles,
      get_vehicle_remarks: ENDPOINTS.remarks,
      get_vehicle_subcategory: ENDPOINTS.subcategory,
      get_vehicle_tracks: ENDPOINTS.tracks
    };

    const endpoint = endpointMap[name];
    if (!endpoint) throw new Error("Tool niet gevonden");

    const data = await fetchRdwData(endpoint, kenteken);
    
    if (data.length === 0) {
      return { content: [{ type: "text", text: `Geen gegevens gevonden voor kenteken: ${kenteken}` }] }]};
    }

    const result = (name === "get_vehicle_info" || name === "get_odometer_judgment") ? data[0] : data;

    return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
  } catch (error: any) {
    return {
      content: [{ type: "text", text: `Fout bij het ophalen van gegevens: ${error.message}` }],
      isError: true,
    };
  }
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
