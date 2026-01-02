# RDW MCP Server (Python Versie)

Een Python-implementatie van de Model Context Protocol (MCP) server voor de RDW Open Data API.

## Installatie

### 1. Kloon de repository en ga naar de Python branch

```bash
git clone https://github.com/djberman87/mcp-rdw-server.git
cd mcp-rdw-server
git checkout python-version
```

### 2. Maak een virtual environment en installeer afhankelijkheden

```bash
python -m venv venv
source venv/bin/activate  # Op Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configureren in Gemini CLI

Voeg de volgende configuratie toe aan je Gemini CLI extensies:

```json
{
  "name": "rdw-python",
  "version": "1.0.0",
  "mcpServers": {
    "rdw": {
      "description": "Zoek kentekengegevens op via de RDW Open Data API (Python).",
      "command": "python",
      "args": ["/PAD/NAAR/mcp-rdw-server/server.py"]
    }
  }
}
```

*Let op: Als je een virtual environment gebruikt, vervang `python` dan door het volledige pad naar het python-executable in je `venv/bin/` map.*

## Gebruik

De werking is identiek aan de JavaScript-versie.

## Licentie

ISC
