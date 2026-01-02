# RDW MCP Server

MCP server voor het ophalen van voertuiggegevens van de Nederlandse RDW Open Data API.

Deze repository bevat implementaties in meerdere talen:

- [Python](./python) (Aanbevolen voor snelle setup met FastMCP)
- [Node.js (JavaScript)](./nodejs)
- [TypeScript](./typescript)

## Functionaliteit

### Tools
- `get_vehicle_info`: Haal technische details op van een voertuig op basis van het kenteken.

## Installatie & Gebruik

### Python
```bash
cd python
pip install -r requirements.txt
python server.py
```

### Node.js (JavaScript)
```bash
cd nodejs
npm install
npm start
```

### TypeScript
```bash
cd typescript
npm install
npm run build
npm start
```

## Licentie
ISC