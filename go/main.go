/**
 * RDW Vehicle Info MCP Server (Go)
 * Authors: Dirk-Jan Berman & Gemini 3
 * Version: 2.0.0
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
	"sync"
)

var ENDPOINTS = map[string]string{
	"info":              "https://opendata.rdw.nl/resource/m9d7-ebf2.json",
	"odometer":          "https://opendata.rdw.nl/resource/v3i9-dpe8.json",
	"fuel":              "https://opendata.rdw.nl/resource/8ys7-d773.json",
	"axles":             "https://opendata.rdw.nl/resource/3huj-srit.json",
	"remarks":           "https://opendata.rdw.nl/resource/7ug8-2dtt.json",
	"subcategory":       "https://opendata.rdw.nl/resource/wj78-6f6f.json",
	"tracks":            "https://opendata.rdw.nl/resource/p693-vshn.json",
	"bodywork":          "https://opendata.rdw.nl/resource/vezc-m2t6.json",
	"bodywork_specific": "https://opendata.rdw.nl/resource/jhie-znh9.json",
	"vehicle_class":     "https://opendata.rdw.nl/resource/kmfi-hrps.json",
}

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

func normalizeKenteken(kenteken string) string {
	k := strings.ToUpper(kenteken)
	k = strings.ReplaceAll(k, "-", "")
	k = strings.ReplaceAll(k, " ", "")
	return k
}

func fetchRdwData(endpoint string, kenteken string) []interface{} {
	resp, err := http.Get(fmt.Sprintf("%s?kenteken=%s", endpoint, kenteken))
	if err != nil {
		return nil
	}
	defer resp.Body.Close()
	body, _ := io.ReadAll(resp.Body)
	var data []interface{}
	json.Unmarshal(body, &data)
	return data
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

		if req.Method == "initialize" {
			sendResponse(req.ID, map[string]interface{}{
				"protocolVersion": "2024-11-05",
				"capabilities":    map[string]interface{}{"tools": map[string]interface{}{}},
				"serverInfo":       map[string]string{"name": "rdw-server-go", "version": "2.0.0"},
			})
		} else if req.Method == "list_tools" {
			sendResponse(req.ID, map[string]interface{}{
				"tools": []map[string]interface{}{
					{"name": "get_vehicle_info", "description": "Haal algemene voertuiggegevens op (Merk, Model, APK, etc.). Dataset: m9d7-ebf2"},
					{"name": "get_odometer_judgment", "description": "Decodeert tellerstand-codes naar tekstuele uitleg (logisch/onlogisch). Dataset: v3i9-dpe8"},
					{"name": "get_vehicle_fuel", "description": "Brandstofverbruik en emissiegegevens. Dataset: 8ys7-d773"},
					{"name": "get_vehicle_axles", "description": "Informatie over de assen van een voertuig (aslasten, aantal assen). Dataset: 3huj-srit"},
					{"name": "get_vehicle_remarks", "description": "Bijzonderheden en specifieke registraties (bijv. taxi, ambulance). Dataset: 7ug8-2dtt"},
					{"name": "get_vehicle_subcategory", "description": "Specifieke voertuig-subcategorie. Dataset: wj78-6f6f"},
					{"name": "get_vehicle_tracks", "description": "Informatie over rupsband-sets. Dataset: p693-vshn"},
					{"name": "get_vehicle_bodywork", "description": "Gecombineerde carrosseriegegevens uit meerdere RDW datasets. Datasets: vezc-m2t6, jhie-znh9, kmfi-hrps"},
				},
			})
		} else if req.Method == "call_tool" {
			var params CallToolParams
			json.Unmarshal(req.Params, &params)

			kenteken := normalizeKenteken(params.Arguments["kenteken"])
			var content string

			if params.Name == "get_vehicle_bodywork" {
				var wg sync.WaitGroup
				var bodywork, specific, vehicleClass []interface{}
				wg.Add(3)
				go func() { defer wg.Done(); bodywork = fetchRdwData(ENDPOINTS["bodywork"], kenteken) }()
				go func() { defer wg.Done(); specific = fetchRdwData(ENDPOINTS["bodywork_specific"], kenteken) }()
				go func() { defer wg.Done(); vehicleClass = fetchRdwData(ENDPOINTS["vehicle_class"], kenteken) }()
				wg.Wait()

				combined := map[string]interface{}{
					"kenteken":              kenteken,
					"carrosserie":           bodywork,
					"carrosserie_specifiek": specific,
					"voertuigklasse":        vehicleClass,
				}
				if len(bodywork) == 0 && len(specific) == 0 && len(vehicleClass) == 0 {
					content = fmt.Sprintf("Geen carrosseriegegevens gevonden voor kenteken: %s", kenteken)
				} else {
					prettyJSON, _ := json.MarshalIndent(combined, "", "  ")
					content = string(prettyJSON)
				}
			} else {
				endpointMap := map[string]string{
					"get_vehicle_info":        ENDPOINTS["info"],
					"get_odometer_judgment":   ENDPOINTS["odometer"],
					"get_vehicle_fuel":        ENDPOINTS["fuel"],
					"get_vehicle_axles":       ENDPOINTS["axles"],
					"get_vehicle_remarks":     ENDPOINTS["remarks"],
					"get_vehicle_subcategory": ENDPOINTS["subcategory"],
					"get_vehicle_tracks":      ENDPOINTS["tracks"],
				}

				endpoint, ok := endpointMap[params.Name]
				if !ok {
					content = "Tool niet gevonden"
				} else {
					data := fetchRdwData(endpoint, kenteken)
					if len(data) == 0 {
						content = fmt.Sprintf("Geen gegevens gevonden voor kenteken: %s", kenteken)
					} else {
						var result interface{} = data
						if params.Name == "get_vehicle_info" || params.Name == "get_odometer_judgment" {
							result = data[0]
						}
						prettyJSON, _ := json.MarshalIndent(result, "", "  ")
						content = string(prettyJSON)
					}
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