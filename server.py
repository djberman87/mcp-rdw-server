import asyncio
import httpx
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
import mcp.types as types

# RDW API Endpoint
RDW_API_ENDPOINT = "https://opendata.rdw.nl/resource/m9d7-ebf2.json"

server = Server("rdw-server-python")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="get_vehicle_info",
            description="Haal informatie op over een voertuig op basis van het kenteken (RDW Open Data).",
            inputSchema={
                "type": "object",
                "properties": {
                    "kenteken": {
                        "type": "string",
                        "description": "Het kenteken van het voertuig (bijv. 41TDK8 of 41-TDK-8). Tekens worden automatisch omgezet naar hoofdletters en streepjes worden verwijderd.",
                    },
                },
                "required": ["kenteken"],
            },
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution requests."""
    if name == "get_vehicle_info":
        if not arguments or "kenteken" not in arguments:
            raise ValueError("Kenteken is verplicht")

        kenteken = str(arguments["kenteken"]).upper().replace("-", "")

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    RDW_API_ENDPOINT,
                    params={"kenteken": kenteken},
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()

                if not data:
                    return [
                        types.TextContent(
                            type="text",
                            text=f"Geen voertuig gevonden met kenteken: {kenteken}"
                        )
                    ]

                import json
                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps(data[0], indent=2)
                    )
                ]
            except Exception as e:
                return [
                    types.TextContent(
                        type="text",
                        text=f"Fout bij het ophalen van voertuiggegevens: {str(e)}"
                    )
                ]
    
    raise ValueError(f"Tool niet gevonden: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="rdw-server-python",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
