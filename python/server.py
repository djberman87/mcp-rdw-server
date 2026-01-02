import asyncio
import httpx
from mcp.server.fastmcp import FastMCP

# Maak een FastMCP server instantie
mcp = FastMCP("RDW Vehicle Info")

RDW_API_ENDPOINT = "https://opendata.rdw.nl/resource/m9d7-ebf2.json"

@mcp.tool()
async def get_vehicle_info(kenteken: str) -> str:
    """
    Haal informatie op over een voertuig op basis van het kenteken (RDW Open Data).
    
    Args:
        kenteken: Het kenteken van het voertuig (bijv. 41TDK8 of 41-TDK-8).
    """
    # Kenteken opschonen: hoofdletters en streepjes verwijderen
    clean_kenteken = kenteken.upper().replace("-", "")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                RDW_API_ENDPOINT,
                params={"kenteken": clean_kenteken},
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            if not data:
                return f"Geen voertuig gevonden met kenteken: {clean_kenteken}"
            
            # Retourneer de eerste match als geformatteerde JSON
            import json
            return json.dumps(data[0], indent=2)
            
        except httpx.HTTPStatusError as e:
            return f"RDW API fout: {e.response.status_code} - {e.response.text}"
        except Exception as e:
            return f"Er is een fout opgetreden: {str(e)}"

if __name__ == "__main__":
    mcp.run()
