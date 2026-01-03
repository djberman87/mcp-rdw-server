# 🚗 RDW Vehicle Info MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP Compliance](https://img.shields.io/badge/MCP-Compliant-blue.svg)](https://modelcontextprotocol.io)
[![Polyglot](https://img.shields.io/badge/Polyglot-8%20Languages-green.svg)](#-ondersteunde-talen)
[![Docker](https://img.shields.io/badge/Docker-GHCR-blue.svg)](https://github.com/djberman87/mcp-rdw-server/pkgs/container/mcp-rdw-server)
[![Dutch Language](https://img.shields.io/badge/Taal-Nederlands-orange.svg)](#)

Een professionele **Model Context Protocol (MCP)** server die directe toegang biedt tot de openbare voertuiggegevens van de Nederlandse **RDW (Rijksdienst voor het Wegverkeer)**. 

---

## 🚀 Distributie & Installatie

Dit project biedt verschillende manieren om de MCP-server te draaien.

### 1. Kant-en-klare Binaries (Aanbevolen)
Geen programmeeromgeving nodig! Download de binary voor jouw OS (Windows, macOS, Linux) van de **[Releases](https://github.com/djberman87/mcp-rdw-server/releases)** pagina.
*   Beschikbaar voor: **Go**, **Rust** en **.NET**.

### 2. Docker (Geen installatie nodig)
Draai de server direct via de GitHub Container Registry:
```json
"rdw-docker": {
  "command": "docker",
  "args": ["run", "-i", "--rm", "ghcr.io/djberman87/mcp-rdw-server:latest"]
}
```

### 3. Handmatige Setup (Polyglot)
Kies de taal die het beste past bij jouw omgeving:

Met deze server kan een LLM (zoals Claude) technische en administratieve details van voertuigen opvragen puur op basis van een kenteken. Ideaal voor automotive applicaties, verzekeringschecks of technische data-analyse.

---

## ✨ Features

- **`get_vehicle_info`**: Haal uitgebreide data op (Merk, Model, APK, Brandstof, CO2, Massa, etc.).
- **`get_vehicle_axles`**: Specifieke as-informatie (Aslast, Aangedreven assen), essentieel voor logistiek/vrachtverkeer.
- **Slimme Normalisatie**: Kentekens zoals `41-TDK-8`, `41TDK8` of `mx xg 82` worden automatisch gecorrigeerd.
- **Polyglot Implementatie**: Beschikbaar in 8 verschillende programmeertalen.

---

### 3. Handmatige Setup (Polyglot)

Kies de taal die het beste past bij jouw omgeving. Kloon de repo en volg de commando's:

| Taal | Directory | Setup Commando | Start Commando |
| :--- | :--- | :--- | :--- |
| 🐍 **Python** | `/python` | `pip install -r requirements.txt` | `python server.py` |
| 🟢 **Node.js** | `/nodejs` | `npm install` | `node index.js` |
| 🔵 **TypeScript** | `/typescript` | `npm install && npm run build` | `node build/index.js` |
| 🐹 **Go** | `/go` | `go mod download` | `go run main.go` |
| 🦀 **Rust** | `/rust` | `cargo build --release` | `./target/release/rust` |
| 🏢 **C#** | `/dotnet` | `dotnet build` | `dotnet run` |
| ☕ **Java** | `/java` | `mvn clean package` | `java -cp target/*.jar com.rdw.McpServer` |
| 🐘 **PHP** | `/php` | `composer install` | `php server.php` |

---

## 🛠️ Configuratie voor Claude Desktop

Voeg de server toe aan je `claude_desktop_config.json`. Gebruik het absolute pad naar de repository.

### Voorbeeld (Python)
```json
{
  "mcpServers": {
    "rdw-info": {
      "command": "python",
      "args": ["/PAD/NAAR/REPO/python/server.py"]
    }
  }
}
```

### Voorbeeld (Node.js)
```json
{
  "mcpServers": {
    "rdw-info": {
      "command": "node",
      "args": ["/PAD/NAAR/REPO/nodejs/index.js"]
    }
  }
}
```

---

## 💡 Voorbeeld Prompts
Zodra de server actief is in Claude, kun je vragen stellen als:
- *"Wat is de APK vervaldatum van het voertuig met kenteken 41-TDK-8?"*
- *"Geef me de technische specificaties (gewicht, motor) van de 23-BGV-9."*
- *"Is het voertuig MX-XG-82 een motor of een auto?"*
- *"Hoeveel assen heeft de vrachtwagen met kenteken ... en wat is de maximale aslast?"*

---

## 📊 RDW Open Data
Dit project maakt gebruik van de officiële Socrata API van de RDW.
- **Hoofd Dataset:** [Open Data RDW: Gekentekende voertuigen](https://opendata.rdw.nl/Voertuigen/Open-Data-RDW-Gekentekende-voertuigen/m9d7-ebf2)
- **Assen Dataset:** [Open Data RDW: Gekentekende voertuigen assen](https://opendata.rdw.nl/Voertuigen/Open-Data-RDW-Gekentekende-voertuigen-assen/3huj-srit)

---

## 👨‍💻 Auteurs & Credits
- **Dirk-Jan Berman** - [GitHub](https://github.com/djberman87) | [LinkedIn](https://www.linkedin.com/in/djberman/)
- **Gemini 3** - AI Architect & Co-Auteur

### Licentie
Gelicenseerd onder de **MIT Licentie**. Zie [LICENSE](./LICENSE) voor details.