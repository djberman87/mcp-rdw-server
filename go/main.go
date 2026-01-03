/**
 * RDW Vehicle Info MCP Server (Go)
 * Authors: Dirk-Jan Berman & Gemini 3
 * License: MIT
 */
package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
)

const RDW_API_ENDPOINT = "https://opendata.rdw.nl/resource/m9d7-ebf2.json"
const RDW_AXLES_API_ENDPOINT = "https://opendata.rdw.nl/resource/3huj-srit.json"

type Request struct {
	JSONRPC string          `json:"jsonrpc"`
	ID      interface{}     `json:"id"`
	Method  string          `json:"method"`
	Params  json.RawMessage `json:"params"`
}

type CallToolParams struct {
	Name      string            `json:"name"`
	Arguments map[string]string `json:"arguments"`
}

func main() {
	reader := bufio.NewReader(os.Stdin)
	for {
		line, err := reader.ReadString('\n')
		if err != nil {
			if err == io.EOF {
				break
			}
			continue
		}

		var req Request
		if err := json.Unmarshal([]byte(line), &req); err != nil {
			continue
		}

		if req.Method == "list_tools" {
			sendResponse(req.ID, map[string]interface{}{
				"tools": []map[string]interface{}{
					{
						"name":        "get_vehicle_info",
						"description": "Haal uitgebreide technische en administratieve informatie op over een Nederlands voertuig (auto, motor, vrachtwagen) via de RDW Open Data API. Gebruik deze tool voor vragen over merk, model, APK-vervaldatum, motorinhoud en milieu-info. Output is in het Nederlands.",
						"inputSchema": map[string]interface{}{
							"type": "object",
							"properties": map[string]interface{}{
								"kenteken": map[string]string{"type": "string", "description": "Het Nederlandse kenteken (bijv. '41TDK8')."},
							},
							"required": []string{"kenteken"},
						},
					},
					{
						"name":        "get_vehicle_axles",
						"description": "Haal specifieke informatie op over de assen van een Nederlands voertuig (vooral voor vrachtwagens/aanhangers). Bevat details over aslast en aangedreven assen. Output is in het Nederlands.",
						"inputSchema": map[string]interface{}{
							"type": "object",
							"properties": map[string]interface{}{
								"kenteken": map[string]string{"type": "string", "description": "Het Nederlandse kenteken (bijv. '23-BGV-9')."},
							},
							"required": []string{"kenteken"},
						},
					},
				},
			})
		} else if req.Method == "call_tool" {
			var params CallToolParams
			json.Unmarshal(req.Params, &params)

			kenteken := strings.ToUpper(strings.ReplaceAll(params.Arguments["kenteken"], "-", ""))
			kenteken = strings.ReplaceAll(kenteken, " ", "")

			endpoint := RDW_API_ENDPOINT
			if params.Name == "get_vehicle_axles" {
				endpoint = RDW_AXLES_API_ENDPOINT
			}

			resp, err := http.Get(fmt.Sprintf("%s?kenteken=%s", endpoint, kenteken))
			var content string
			if err != nil {
				content = fmt.Sprintf("Fout bij verbinden met RDW: %v", err)
			} else {
				defer resp.Body.Close()
				body, _ := io.ReadAll(resp.Body)
				var data []interface{}
				json.Unmarshal(body, &data)

				if len(data) == 0 {
					if params.Name == "get_vehicle_info" {
						content = fmt.Sprintf("Geen voertuig gevonden voor kenteken: %s", kenteken)
					} else {
						content = fmt.Sprintf("Geen as-informatie gevonden voor kenteken: %s. Let op: lichte personenauto's hebben vaak geen vermelding in deze dataset.", kenteken)
					}
				} else {
					var result interface{} = data
					if params.Name == "get_vehicle_info" {
						result = data[0]
					}
					prettyJSON, _ := json.MarshalIndent(result, "", "  ")
					content = string(prettyJSON)
				}
			}

			sendResponse(req.ID, map[string]interface{}{
				"content": []map[string]interface{}{
					{"type": "text", "text": content},
				},
			})
		}
	}
}

func sendResponse(id interface{}, result interface{}) {
	resp := map[string]interface{}{
		"jsonrpc": "2.0",
		"id":      id,
		"result":  result,
	}
	out, _ := json.Marshal(resp)
	fmt.Println(string(out))
}