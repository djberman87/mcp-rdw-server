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
    Haal uitgebreide technische en administratieve informatie op over een Nederlands voertuig (zoals auto, motor, vrachtwagen) via de RDW Open Data API.
    
    Gebruik deze tool voor vragen over:
    - Basisdetails: Merk, model (handelsbenaming), kleur, voertuigsoort.
    - Status: Vervaldatum APK, of het voertuig gestolen is, of er een WOK-status (Wacht Op Keuren) is.
    - Techniek: Motorinhoud, aantal cilinders, massa rijklaar, trekvermogen.
    - Milieu: Brandstofverbruik, CO2-uitstoot, emissieklasse.
    
    Args:
        kenteken: Het Nederlandse kenteken (bijv. '41TDK8', '41-TDK-8' of 'MX-XG-82'). 
                  Spaties en streepjes worden automatisch verwijderd.
    
    Returns:
        Een JSON-geformatteerde string met alle beschikbare gegevens van de RDW. De veldnamen zijn in het Nederlands.
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
    Haal specifieke informatie op over de assen van een Nederlands voertuig via de RDW Open Data API.
    
    Gebruik deze tool specifiek voor:
    - Technische as-details: Aantal assen, aslast (maximaal toegestane massa), aangedreven assen.
    - Configuratie: Afstand tussen de assen, spoorbreedte.
    
    Let op: Deze dataset is vooral relevant voor vrachtwagens, aanhangers en zware voertuigen. 
    Voor lichte personenauto's is deze informatie vaak niet beschikbaar in deze specifieke dataset.
    
    Args:
        kenteken: Het Nederlandse kenteken (bijv. '23-BGV-9').
    
    Returns:
        Een JSON-geformatteerde lijst met informatie per as. Veldnamen zijn in het Nederlands.
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
