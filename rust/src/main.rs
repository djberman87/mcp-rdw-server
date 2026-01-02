/**
 * RDW Vehicle Info MCP Server (Rust)
 * Authors: Dirk-Jan Berman & Gemini 3
 * License: MIT
 */
use serde::{Deserialize, Serialize};
use std::error::Error;
use std::io::{self, BufRead};

#[derive(Deserialize)]
struct GetVehicleInfoArgs {
    kenteken: String,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    let stdin = io::stdin();
    let mut reader = stdin.lock().lines();

    // Simpele Stdio implementatie voor MCP
    while let Some(line) = reader.next() {
        let request: serde_json::Value = serde_json::from_str(&line?)?;
        
        if request["method"] == "list_tools" {
            let response = serde_json::json!({
                "jsonrpc": "2.0",
                "id": request["id"],
                "result": {
                    "tools": [
                        {
                            "name": "get_vehicle_info",
                            "description": "Haal gedetailleerde technische informatie op over een Nederlands voertuig op basis van het kenteken.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "kenteken": {
                                        "type": "string",
                                        "description": "Het kenteken van het voertuig (bijv. '41TDK8')."
                                    }
                                },
                                "required": ["kenteken"]
                            }
                        }
                    ]
                }
            });
            println!("{}", response);
        } else if request["method"] == "call_tool" && request["params"]["name"] == "get_vehicle_info" {
            let kenteken = request["params"]["arguments"]["kenteken"]
                .as_str()
                .unwrap_or("")
                .to_uppercase()
                .replace("-", "")
                .replace(" ", "");

            let url = format!("https://opendata.rdw.nl/resource/m9d7-ebf2.json?kenteken={}", kenteken);
            let client = reqwest::Client::new();
            let res = client.get(url).send().await?.json::<Vec<serde_json::Value>>().await?;

            let content = if res.is_empty() {
                format!("Geen voertuig gevonden voor kenteken: {}", kenteken)
            } else {
                serde_json::to_string_pretty(&res[0])?
            };

            let response = serde_json::json!({
                "jsonrpc": "2.0",
                "id": request["id"],
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": content
                        }
                    ]
                }
            });
            println!("{}", response);
        }
    }

    Ok(())
}
