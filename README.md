# 🚗 RDW Vehicle Info MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP Compliance](https://img.shields.io/badge/MCP-Compliant-blue.svg)](https://modelcontextprotocol.io)
[![Polyglot](https://img.shields.io/badge/Polyglot-8%20Languages-green.svg)](#-ondersteunde-talen)

Een krachtige **Model Context Protocol (MCP)** server die directe toegang biedt tot de openbare voertuiggegevens van de Nederlandse **RDW (Rijksdienst voor het Wegverkeer)**. 

Met deze server kan een LLM (zoals Claude) technische details van voertuigen opvragen, zoals merk, model, APK-vervaldatum, brandstofverbruik en meer, puur op basis van een kenteken.

---

## ✨ Functionaliteit

### Tools
- `get_vehicle_info`: Haal gedetailleerde technische informatie op van elk Nederlands voertuig (auto's, motoren, vrachtwagens, etc.).
  - **Input:** Kenteken (bijv. `41TDK8`, `41-TDK-8`, `MX-XG-82`).
  - **Normalisatie:** Tekens worden automatisch omgezet naar hoofdletters en streepjes/spaties worden verwijderd.
- `get_vehicle_axles`: Haal gedetailleerde informatie op over de assen van een voertuig (aantal assen, aslast, aangedreven assen).
  - **Input:** Kenteken.
  - **Dataset:** Specifiek gericht op de as-configuratie van zwaardere voertuigen en aanhangers.

---

## 🚀 Ondersteunde Talen & Runtimes

Dit project is een **polyglot showcase**. Kies de taal die het beste past bij jouw omgeving. Voor Go, Rust en .NET zijn **kant-en-klare binaries** beschikbaar bij de [Releases](https://github.com/djberman87/mcp-rdw-server/releases).

| Taal | Runtime/Manager | Locatie | Setup / Binary |
| :--- | :--- | :--- | :--- |
| 🐍 **Python** | Python 3.10+ | [`/python`](./python) | `pip install -r requirements.txt` |
| 🟢 **Node.js** | Node 18+ | [`/nodejs`](./nodejs) | `npm install` |
| 🔵 **TypeScript** | Node 18+ | [`/typescript`](./typescript) | `npm install && npm run build` |
| 🐹 **Go** | Go 1.21+ | [`/go`](./go) | `go mod download` of **Binary** |
| 🦀 **Rust** | Rust 1.75+ | [`/rust`](./rust) | `cargo build --release` of **Binary** |
| 🏢 **C#** | .NET 8.0 | [`/dotnet`](./dotnet) | `dotnet build` of **Binary** |
| ☕ **Java** | Maven / JDK 17 | [`/java`](./java) | `mvn clean package` |
| 🐘 **PHP** | PHP 8.1+ | [`/php`](./php) | `composer install` |

---

## 🛠️ Installatie & Configuratie

### 1. Voorbereiding
Zorg dat de gekozen runtime is geïnstalleerd op je systeem.

### 2. Claude Desktop Configuratie
Voeg de server toe aan je `claude_desktop_config.json`. Vervang `<PATH_TO_REPO>` door het absolute pad naar deze repository.

**Voorbeeld met Python (FastMCP):**
```json
{
  "mcpServers": {
    "rdw-info": {
      "command": "python",
      "args": ["<PATH_TO_REPO>/python/server.py"]
    }
  }
}
```

**Voorbeeld met Node.js:**
```json
{
  "mcpServers": {
    "rdw-info": {
      "command": "node",
      "args": ["<PATH_TO_REPO>/nodejs/index.js"]
    }
  }
}
```

---

## 📊 RDW Open Data
Deze server maakt uitsluitend gebruik van de **officiële openbare RDW API**. Er is **geen API-key** nodig voor basisgebruik.

- **Basis Dataset:** `https://opendata.rdw.nl/resource/m9d7-ebf2.json` (Gekentekende voertuigen)
- **Assen Dataset:** `https://opendata.rdw.nl/resource/3huj-srit.json` (Gekentekende voertuigen assen)
- **Documentatie:** [RDW Open Data Portal](https://opendata.rdw.nl/)

---

## 👨‍💻 Auteurs & Metadata
- **Dirk-Jan Berman** - [GitHub](https://github.com/djberman87) | [LinkedIn](https://www.linkedin.com/in/djberman/)
- **Gemini 3** - AI Co-Auteur & Architect

### Licentie
Dit project valt onder de **MIT Licentie**. Zie het [LICENSE](./LICENSE) bestand voor details.

---

> *Geoptimaliseerd voor Model Context Protocol door Gemini 3 op 2 januari 2026.*
