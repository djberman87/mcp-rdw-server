"""
RDW Vehicle Info MCP Server
Authors: Dirk-Jan Berman & Gemini 3
Version: 2.0.0
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

# API Endpoints
ENDPOINTS = {
    "info": "https://opendata.rdw.nl/resource/m9d7-ebf2.json",
    "odometer": "https://opendata.rdw.nl/resource/v3i9-dpe8.json",
    "fuel": "https://opendata.rdw.nl/resource/8ys7-d773.json",
    "axles": "https://opendata.rdw.nl/resource/3huj-srit.json",
    "remarks": "https://opendata.rdw.nl/resource/7ug8-2dtt.json",
    "subcategory": "https://opendata.rdw.nl/resource/wj78-6f6f.json",
    "tracks": "https://opendata.rdw.nl/resource/p693-vshn.json",
    "bodywork": "https://opendata.rdw.nl/resource/vezc-m2t6.json",
    "bodywork_specific": "https://opendata.rdw.nl/resource/jhie-znh9.json",
    "vehicle_class": "https://opendata.rdw.nl/resource/kmfi-hrps.json"
}

def normalize_kenteken(kenteken: str) -> str:
    """Normalizeert het kenteken naar UPPERCASE zonder streepjes of spaties."""
    return kenteken.upper().replace("-", "").replace(" ", "")

async def fetch_rdw_data(client: httpx.AsyncClient, endpoint: str, kenteken: str):
    """Hulpfunctie om data op te halen van een RDW endpoint."""
    try:
        response = await client.get(
            endpoint,
            params={"kenteken": kenteken},
            timeout=10.0
        )
        response.raise_for_status()
        return response.json()
    except Exception:
        return []

@mcp.tool()
async def get_vehicle_info(kenteken: str) -> str:
    """
    Haal algemene voertuiggegevens op (Merk, Model, APK, etc.).
    Dataset: m9d7-ebf2
    """
    clean_kenteken = normalize_kenteken(kenteken)
    async with httpx.AsyncClient() as client:
        data = await fetch_rdw_data(client, ENDPOINTS["info"], clean_kenteken)
        if not data:
            return f"Geen voertuig gevonden voor kenteken: {clean_kenteken}"
        return json.dumps(data[0], indent=2)

@mcp.tool()
async def get_odometer_judgment(kenteken: str) -> str:
    """
    Decodeert tellerstand-codes naar tekstuele uitleg (logisch/onlogisch).
    Dataset: v3i9-dpe8
    """
    clean_kenteken = normalize_kenteken(kenteken)
    async with httpx.AsyncClient() as client:
        data = await fetch_rdw_data(client, ENDPOINTS["odometer"], clean_kenteken)
        if not data:
            return f"Geen tellerstand oordeel gevonden voor kenteken: {clean_kenteken}"
        return json.dumps(data[0], indent=2)

@mcp.tool()
async def get_vehicle_fuel(kenteken: str) -> str:
    """
    Brandstofverbruik en emissiegegevens.
    Dataset: 8ys7-d773
    """
    clean_kenteken = normalize_kenteken(kenteken)
    async with httpx.AsyncClient() as client:
        data = await fetch_rdw_data(client, ENDPOINTS["fuel"], clean_kenteken)
        if not data:
            return f"Geen brandstofgegevens gevonden voor kenteken: {clean_kenteken}"
        return json.dumps(data, indent=2)

@mcp.tool()
async def get_vehicle_axles(kenteken: str) -> str:
    """
    Informatie over de assen van een voertuig (aslasten, aantal assen).
    Dataset: 3huj-srit
    """
    clean_kenteken = normalize_kenteken(kenteken)
    async with httpx.AsyncClient() as client:
        data = await fetch_rdw_data(client, ENDPOINTS["axles"], clean_kenteken)
        if not data:
            return f"Geen as-informatie gevonden voor kenteken: {clean_kenteken}"
        return json.dumps(data, indent=2)

@mcp.tool()
async def get_vehicle_remarks(kenteken: str) -> str:
    """
    Bijzonderheden en specifieke registraties (bijv. taxi, ambulance).
    Dataset: 7ug8-2dtt
    """
    clean_kenteken = normalize_kenteken(kenteken)
    async with httpx.AsyncClient() as client:
        data = await fetch_rdw_data(client, ENDPOINTS["remarks"], clean_kenteken)
        if not data:
            return f"Geen opmerkingen gevonden voor kenteken: {clean_kenteken}"
        return json.dumps(data, indent=2)

@mcp.tool()
async def get_vehicle_subcategory(kenteken: str) -> str:
    """
    Specifieke voertuig-subcategorie.
    Dataset: wj78-6f6f
    """
    clean_kenteken = normalize_kenteken(kenteken)
    async with httpx.AsyncClient() as client:
        data = await fetch_rdw_data(client, ENDPOINTS["subcategory"], clean_kenteken)
        if not data:
            return f"Geen subcategorie gevonden voor kenteken: {clean_kenteken}"
        return json.dumps(data, indent=2)

@mcp.tool()
async def get_vehicle_tracks(kenteken: str) -> str:
    """
    Informatie over rupsband-sets.
    Dataset: p693-vshn
    """
    clean_kenteken = normalize_kenteken(kenteken)
    async with httpx.AsyncClient() as client:
        data = await fetch_rdw_data(client, ENDPOINTS["tracks"], clean_kenteken)
        if not data:
            return f"Geen rupsband informatie gevonden voor kenteken: {clean_kenteken}"
        return json.dumps(data, indent=2)

@mcp.tool()
async def get_vehicle_bodywork(kenteken: str) -> str:
    """
    Gecombineerde carrosseriegegevens uit meerdere RDW datasets.
    Datasets: vezc-m2t6 (Basis), jhie-znh9 (Specifiek), kmfi-hrps (Klasse)
    """
    clean_kenteken = normalize_kenteken(kenteken)
    async with httpx.AsyncClient() as client:
        # Parallel ophalen van alle carrosserie data
        tasks = [
            fetch_rdw_data(client, ENDPOINTS["bodywork"], clean_kenteken),
            fetch_rdw_data(client, ENDPOINTS["bodywork_specific"], clean_kenteken),
            fetch_rdw_data(client, ENDPOINTS["vehicle_class"], clean_kenteken)
        ]
        results = await asyncio.gather(*tasks)
        
        combined_data = {
            "kenteken": clean_kenteken,
            "carrosserie": results[0],
            "carrosserie_specifiek": results[1],
            "voertuigklasse": results[2]
        }
        
        if not any(results):
            return f"Geen carrosseriegegevens gevonden voor kenteken: {clean_kenteken}"
            
        return json.dumps(combined_data, indent=2)

if __name__ == "__main__":
    mcp.run()
