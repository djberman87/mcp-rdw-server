# 🤖 Gemini Project Metadata

This project, the **RDW Vehicle Info MCP Server**, was architected and implemented with the assistance of **Gemini**.

## 🧬 AI Role & Contributions
- **Architectural Design:** Designed the polyglot structure supporting 8 different runtimes (Python, Node.js, TypeScript, Go, Rust, .NET, Java, PHP).
- **Implementation:** Generated the core logic for vehicle data retrieval, license plate normalization, and MCP tool definitions across all supported languages.
- **Optimization:** Ensured consistent behavior and standardized tool naming across the various implementations.
- **Documentation:** Authored the comprehensive README and language-specific instructions.

## 🏗️ Polyglot Strategy
The project serves as a showcase for how the Model Context Protocol (MCP) can be implemented across diverse ecosystems. Gemini ensured that:
1. Each implementation follows the idiomatic patterns of its respective language.
2. The `get_vehicle_info` and `get_vehicle_axles` tools provide identical functionality regardless of the backend chosen.
3. Common normalization logic is applied to Dutch license plates (Kentekens) consistently.

## 🛠️ Tech Stack Notes
- **Protocol:** Model Context Protocol (MCP)
- **Data Source:** RDW Open Data (Netherlands)
- **Languages:** Python, JavaScript, TypeScript, Go, Rust, C#, Java, PHP.

---
*Created by Gemini 3 on January 3, 2026.*
