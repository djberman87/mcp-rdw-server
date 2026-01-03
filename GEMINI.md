# 🤖 Gemini Project Metadata

This project, the **RDW Vehicle Info MCP Server**, was architected and implemented with the assistance of **Gemini**.

## 🧬 AI Role & Contributions
- **Architectural Design:** Designed the polyglot structure supporting 8 different runtimes (Python, Node.js, TypeScript, Go, Rust, .NET, Java, PHP).
- **Implementation:** Generated the core logic for vehicle data retrieval, relational dataset linking, license plate normalization, and MCP tool definitions across all supported languages.
- **Optimization:** Ensured consistent behavior and standardized tool naming across the various implementations.
- **Containerization:** Implemented Docker support for seamless deployment via GHCR.
- **Documentation:** Authored the comprehensive README, technical guides, and multi-language instructions.

## 🏗️ Polyglot Strategy
The project serves as a showcase for how the Model Context Protocol (MCP) can be implemented across diverse ecosystems. Gemini ensured that:
1. Each implementation follows the idiomatic patterns of its respective language.
2. The complete v2.0.0 toolset is consistently implemented across backends, including:
    - **Core:** `get_vehicle_info`, `get_odometer_judgment`
    - **Technical:** `get_vehicle_fuel`, `get_vehicle_axles`, `get_vehicle_remarks`, `get_vehicle_subcategory`, `get_vehicle_tracks`
    - **Relational:** `get_vehicle_bodywork` (aggregating data from multiple RDW datasets)
3. Common normalization logic is applied to Dutch license plates (Kentekens) consistently.

## 🛠️ Tech Stack Notes
- **Protocol:** Model Context Protocol (MCP) v1.3.1
- **Data Source:** RDW Open Data (Netherlands)
- **Languages:** Python, JavaScript, TypeScript, Go, Rust, C#, Java, PHP.
- **Deployment:** Docker (GHCR), GitHub Releases (Binaries).

---
*Last updated by Gemini 3 on January 3, 2026 (v2.0.0 Verified).*