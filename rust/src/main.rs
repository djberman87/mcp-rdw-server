/**
 * RDW Vehicle Info MCP Server (Rust)
 * Authors: Dirk-Jan Berman & Gemini 3
 * Version: 2.0.0
 * License: MIT
 */
use serde_json::json;
use std::collections::HashMap;
use std::error::Error;
use std::io::{self, BufRead};

async fn fetch_rdw_data(client: &reqwest::Client, endpoint: &str, kenteken: &str) -> Vec<serde_json::Value> {
    let url = format!("{}?kenteken={}", endpoint, kenteken);
    match client.get(url).send().await {
        Ok(res) => res.json::<Vec<serde_json::Value>>().await.unwrap_or_else(|_| vec![]),
        Err(_) => vec![],
    }
}

fn normalize_kenteken(kenteken: &str) -> String {
    kenteken.to_uppercase().replace("-", "").replace(" ", "")
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    let stdin = io::stdin();
    let mut reader = stdin.lock().lines();
    let client = reqwest::Client::new();

    let endpoints: HashMap<&str, &str> = [
        ("info", "https://opendata.rdw.nl/resource/m9d7-ebf2.json"),
        ("odometer", "https://opendata.rdw.nl/resource/v3i9-dpe8.json"),
        ("fuel", "https://opendata.rdw.nl/resource/8ys7-d773.json"),
        ("axles", "https://opendata.rdw.nl/resource/3huj-srit.json"),
        ("remarks", "https://opendata.rdw.nl/resource/7ug8-2dtt.json"),
        ("subcategory", "https://opendata.rdw.nl/resource/wj78-6f6f.json"),
        ("tracks", "https://opendata.rdw.nl/resource/p693-vshn.json"),
        ("bodywork", "https://opendata.rdw.nl/resource/vezc-m2t6.json"),
        ("bodywork_specific", "https://opendata.rdw.nl/resource/jhie-znh9.json"),
        ("vehicle_class", "https://opendata.rdw.nl/resource/kmfi-hrps.json"),
    ].iter().cloned().collect();

    while let Some(line) = reader.next() {
        let request: serde_json::Value = serde_json::from_str(&line?)?;
        
        if request["method"] == "initialize" {
            let response = json!({
                "jsonrpc": "2.0",
                "id": request["id"],
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "rdw-server-rust", "version": "2.0.0"}
                }
            });
            println!("{}", response);
        } else if request["method"] == "list_tools" {
            let response = json!({
                "jsonrpc": "2.0",
                "id": request["id"],
                "result": {
                    "tools": [
                        {"name": "get_vehicle_info", "description": "Haal algemene voertuiggegevens op (Merk, Model, APK, etc.). Dataset: m9d7-ebf2"},
                        {"name": "get_odometer_judgment", "description": "Decodeert tellerstand-codes naar tekstuele uitleg (logisch/onlogisch). Dataset: v3i9-dpe8"},
                        {"name": "get_vehicle_fuel", "description": "Brandstofverbruik en emissiegegevens. Dataset: 8ys7-d773"},
                        {"name": "get_vehicle_axles", "description": "Informatie over de assen van een voertuig (aslasten, aantal assen). Dataset: 3huj-srit"},
                        {"name": "get_vehicle_remarks", "description": "Bijzonderheden en specifieke registraties (bijv. taxi, ambulance). Dataset: 7ug8-2dtt"},
                        {"name": "get_vehicle_subcategory", "description": "Specifieke voertuig-subcategorie. Dataset: wj78-6f6f"},
                        {"name": "get_vehicle_tracks", "description": "Informatie over rupsband-sets. Dataset: p693-vshn"},
                        {"name": "get_vehicle_bodywork", "description": "Gecombineerde carrosseriegegevens uit meerdere RDW datasets. Datasets: vezc-m2t6, jhie-znh9, kmfi-hrps"}
                    ]
                }
            });
            println!("{}", response);
        } else if request["method"] == "call_tool" {
            let tool_name = request["params"]["name"].as_str().unwrap_or("");
            let kenteken = normalize_kenteken(request["params"]["arguments"]["kenteken"].as_str().unwrap_or(""));

            let content = if tool_name == "get_vehicle_bodywork" {
                let (b, s, c) = tokio::join!(
                    fetch_rdw_data(&client, endpoints["bodywork"], &kenteken),
                    fetch_rdw_data(&client, endpoints["bodywork_specific"], &kenteken),
                    fetch_rdw_data(&client, endpoints["vehicle_class"], &kenteken)
                );
                
                if b.is_empty() && s.is_empty() && c.is_empty() {
                    format!("Geen carrosseriegegevens gevonden voor kenteken: {}", kenteken)
                } else {
                    let combined = json!({
                        "kenteken": kenteken,
                        "carrosserie": b,
                        "carrosserie_specifiek": s,
                        "voertuigklasse": c
                    });
                    serde_json::to_string_pretty(&combined)?
                }
            } else {
                let endpoint = match tool_name {
                    "get_vehicle_info" => endpoints["info"],
                    "get_odometer_judgment" => endpoints["odometer"],
                    "get_vehicle_fuel" => endpoints["fuel"],
                    "get_vehicle_axles" => endpoints["axles"],
                    "get_vehicle_remarks" => endpoints["remarks"],
                    "get_vehicle_subcategory" => endpoints["subcategory"],
                    "get_vehicle_tracks" => endpoints["tracks"],
                    _ => "",
                };

                if endpoint.is_empty() {
                    "Tool niet gevonden".to_string()
                } else {
                    let data = fetch_rdw_data(&client, endpoint, &kenteken).await;
                    if data.is_empty() {
                        format!("Geen gegevens gevonden voor kenteken: {}", kenteken)
                    } else {
                        if tool_name == "get_vehicle_info" || tool_name == "get_odometer_judgment" {
                            serde_json::to_string_pretty(&data[0])?
                        } else {
                            serde_json::to_string_pretty(&data)?
                        }
                    }
                }
            };

            let response = json!({
                "jsonrpc": "2.0",
                "id": request["id"],
                "result": {
                    "content": [{"type": "text", "text": content}]
                }
            });
            println!("{}", response);
        }
    }
    Ok(())
}
