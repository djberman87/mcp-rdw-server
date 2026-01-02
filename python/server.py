"""
RDW Vehicle Info MCP Server
Authors: Dirk-Jan Berman & Gemini 3
License: MIT
"""

import asyncio
import httpx
import json
from mcp.server.fastmcp import FastMCP

# Maak een FastMCP server instantie
mcp = FastMCP(
    "RDW Vehicle Info",
    dependencies=["httpx"]
)

RDW_API_ENDPOINT = "https://opendata.rdw.nl/resource/m9d7-ebf2.json"
RDW_AXLES_API_ENDPOINT = "https://opendata.rdw.nl/resource/3huj-srit.json"

@mcp.tool()
async def get_vehicle_info(kenteken: str) -> str:
    """
    Haal gedetailleerde technische informatie op over een Nederlands voertuig op basis van het kenteken.
    
    Args:
        kenteken: Het kenteken van het voertuig (bijv. '41TDK8', '41-TDK-8' of '23BGV9'). 
                  Tekens worden automatisch genormaliseerd (hoofdletters, streepjes verwijderd).
    
    Returns:
        Een JSON-string met voertuiggegevens zoals merk, model, brandstofverbruik, vervaldatum APK, etc.
    """
    # Kenteken opschonen: hoofdletters en streepjes verwijderen
    clean_kenteken = kenteken.upper().replace("-", "").replace(" ", "")
    
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
                return f"Geen voertuig gevonden voor kenteken: {clean_kenteken}"
            
            # Retourneer de eerste match als geformatteerde JSON
            return json.dumps(data[0], indent=2)
            
        except httpx.HTTPStatusError as e:
            return f"RDW API fout: {e.response.status_code} - {e.response.text}"
        except asyncio.TimeoutError:
            return "Fout: De RDW API reageerde niet binnen de tijdlimiet."
        except Exception as e:
            return f"Er is een onverwachte fout opgetreden: {str(e)}"

@mcp.tool()
async def get_vehicle_axles(kenteken: str) -> str:
    """
    Haal informatie op over de assen van een voertuig op basis van het kenteken.
    
    Args:
        kenteken: Het kenteken van het voertuig (bijv. '41TDK8').
    
    Returns:
        Een JSON-string met as-informatie zoals aantal assen, aslast, aangedreven assen, etc.
    """
    clean_kenteken = kenteken.upper().replace("-", "").replace(" ", "")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                RDW_AXLES_API_ENDPOINT,
                params={"kenteken": clean_kenteken},
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            if not data:
                return f"Geen as-informatie gevonden voor kenteken: {clean_kenteken}. Let op: lichte personenauto's hebben vaak geen vermelding in deze dataset."
            
            return json.dumps(data, indent=2)
            
        except httpx.HTTPStatusError as e:
            return f"RDW API fout: {e.response.status_code} - {e.response.text}"
        except asyncio.TimeoutError:
            return "Fout: De RDW API reageerde niet binnen de tijdlimiet."
        except Exception as e:
            return f"Er is een onverwachte fout opgetreden: {str(e)}"

if __name__ == "__main__":
    mcp.run()

if __name__ == "__main__":
    mcp.run()
