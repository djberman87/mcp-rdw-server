# RDW MCP Server

Een Model Context Protocol (MCP) server voor het ophalen van voertuiggegevens via de RDW Open Data API.

## Mogelijkheden

- **get_vehicle_info**: Haal uitgebreide informatie op over een voertuig op basis van het kenteken.

## Installatie

### 1. Kloon de repository

```bash
git clone https://github.com/djberman87/mcp-rdw-server.git
cd mcp-rdw-server
```

### 2. Installeer afhankelijkheden

```bash
npm install
```

### 3. Configureren in Gemini CLI

Voeg de volgende configuratie toe aan je Gemini CLI extensies (meestal in `~/.gemini/extensions/rdw/gemini-extension.json` of een vergelijkbare locatie):

```json
{
  "name": "rdw",
  "version": "1.0.0",
  "mcpServers": {
    "rdw": {
      "description": "Zoek kentekengegevens op via de RDW Open Data API.",
      "command": "node",
      "args": ["/PAD/NAAR/mcp-rdw-server/index.js"]
    }
  }
}
```

*Vervang `/PAD/NAAR/` door het daadwerkelijke pad naar de gedownloade map.*

## Gebruik

Zodra de server actief is in Gemini CLI, kun je simpelweg vragen om voertuiggegevens:

- "Wat zijn de gegevens van kenteken 41-TDK-8?"
- "Zoek kenteken MXXG82 op."

## Licentie

ISC
