import asyncio
import json
from python.server import mcp

async def run_tests():
    test_kentekens = ["BB943Z", "41TDK8", "AL0645", "OV69ZV"]
    
    print("=== TEST 1: get_vehicle_axles ===")
    for k in test_kentekens:
        print(f"\n--- Testing Axles for: {k} ---")
        try:
            result = await mcp.call_tool("get_vehicle_axles", {"kenteken": k})
            print(result[0][0].text)
        except Exception as e:
            print(f"Error: {e}")

    print("\n\n=== TEST 2: Combined (Info + Axles) ===")
    for k in test_kentekens[:2]: # Test met de eerste twee voor de gecombineerde test
        print(f"\n--- Combined Info for: {k} ---")
        try:
            info = await mcp.call_tool("get_vehicle_info", {"kenteken": k})
            axles = await mcp.call_tool("get_vehicle_axles", {"kenteken": k})
            
            # Print een samenvatting
            info_data = json.loads(info[0][0].text)
            axle_data = json.loads(axles[0][0].text)
            
            brand = info_data.get("merk", "Onbekend")
            model = info_data.get("handelsbenaming", "Onbekend")
            print(f"Voertuig: {brand} {model}")
            print(f"Aantal assen: {len(axle_data)}")
            for i, a in enumerate(axle_data):
                as_last = a.get("wettelijk_toegestane_maximum_aslast", "N/A")
                print(f"  As {i+1}: {as_last} kg")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(run_tests())