# 🚗 RDW Vehicle Info MCP Server

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP Compliance](https://img.shields.io/badge/MCP-Compliant-blue.svg)](https://modelcontextprotocol.io)
[![Polyglot](https://img.shields.io/badge/Polyglot-8%20Languages-green.svg)](#-handmatige-setup-polyglot)
[![Docker](https://img.shields.io/badge/Docker-GHCR-blue.svg)](https://github.com/djberman87/mcp-rdw-server/pkgs/container/mcp-rdw-server)

Een professionele **Model Context Protocol (MCP)** server die directe toegang biedt tot de openbare voertuiggegevens van de Nederlandse **RDW (Rijksdienst voor het Wegverkeer)**. 

Versie 2.0.0 introduceert een volledige relationele implementatie, waarbij data uit verschillende RDW-datasets wordt gekoppeld op basis van het kenteken.

---

## ✨ Features (v2.0.0 Tools)

### 1. Basisinformatie & Status
- **`get_vehicle_info`**: Algemene voertuiggegevens (Merk, Model, APK, etc.).
- **`get_odometer_judgment`**: Decodeert tellerstand-codes naar tekstuele uitleg (logisch/onlogisch).

### 2. Technische Datasets
- **`get_vehicle_fuel`**: Brandstofverbruik en emissiegegevens.
- **`get_vehicle_axles`**: As-informatie en lasten (essentieel voor zwaar vervoer).
- **`get_vehicle_remarks`**: Bijzonderheden en specifieke registraties.
- **`get_vehicle_subcategory`**: Specifieke voertuig-subcategorie.
- **`get_vehicle_tracks`**: Informatie over rupsband-sets.

### 3. Carrosserie Cluster (Relationeel)
- **`get_vehicle_bodywork`**: Combineert data uit drie verschillende datasets (Basis, Specifiek, Klasse) tot één compleet carrosserie-object.

---

## 🔗 Relationele Structuur
De RDW-data is relationeel opgebouwd. In Versie 2.0.0 worden de volgende koppelingen automatisch afgehandeld:
- **Directe koppeling:** De meeste tools halen data op via een directe query op het kenteken.
- **Geaggregeerde Carrosserie:** De tool `get_vehicle_bodywork` combineert data uit `vezc-m2t6` (Carrosserie), `jhie-znh9` (Specifiek) en `kmfi-hrps` (Klasse) om een integraal beeld van het voertuig te geven.

---

## 🚀 Distributie & Installatie

Dit project biedt verschillende manieren om de MCP-server te draaien, afhankelijk van je behoeften.

### 1. Kant-en-klare Binaries (Snelst)
Geen programmeeromgeving nodig. Download de binary voor jouw OS (Windows, macOS, Linux) van de **[Releases](https://github.com/djberman87/mcp-rdw-server/releases)** pagina.
*   **Techniek:** Geoptimaliseerde builds in **Go**, **Rust** of **.NET**.

### 2. Docker (Cloud & Server)
Draai de server als container zonder lokale dependencies:
```json
"rdw-docker": {
  "command": "docker",
  "args": ["run", "-i", "--rm", "ghcr.io/djberman87/mcp-rdw-server:latest"]
}
```

### 3. Handmatige Setup (Polyglot)
Kies de taal die het beste past bij jouw stack. Kloon de repository en volg de commando's:

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

Voeg de server toe aan je `claude_desktop_config.json`. Gebruik het **absolute pad** naar de executable of het script.

### Voorbeeld (Python/FastMCP)
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
Zodra de server actief is, kun je Claude vragen stellen zoals:
- *"Is de tellerstand van het voertuig met kenteken 41-TDK-8 logisch verklaard volgens de RDW?"*
- *"Geef me de uitgebreide carrosseriegegevens en de voertuigklasse van de BB-943-Z."*
- *"Wat is de maximale aslast van de verschillende assen voor de vrachtwagen met kenteken ...?"*
- *"Hoeveel zitplaatsen heeft de touringcar met kenteken ... en wat is de geregistreerde hoogte van het voertuig?"*
- *"Wat zijn de milieugegevens (emissieklasse en brandstofverbruik) van de 23-BGV-9?"*
- *"Geef een overzicht van alle technische bijzonderheden (remarks) voor kenteken ..."*

---

## 📊 RDW Open Data
Dit project maakt gebruik van de officiële Socrata API van de RDW.
- **Hoofd Dataset:** [Gekentekende voertuigen](https://opendata.rdw.nl/Voertuigen/Open-Data-RDW-Gekentekende-voertuigen/m9d7-ebf2)
- **Assen Dataset:** [Gekentekende voertuigen assen](https://opendata.rdw.nl/Voertuigen/Open-Data-RDW-Gekentekende-voertuigen-assen/3huj-srit)

---

## 👨‍💻 Auteurs & Credits
- **Dirk-Jan Berman** - [GitHub](https://github.com/djberman87) | [LinkedIn](https://www.linkedin.com/in/djberman/)
- **Gemini 3** - AI Architect & Co-Auteur

### Licentie
Gelicenseerd onder de **MIT Licentie**. Zie [LICENSE](./LICENSE) voor details.
