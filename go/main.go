/**
 * RDW Vehicle Info MCP Server (Go)
 * Authors: Dirk-Jan Berman & Gemini 3
 * License: MIT
 */
package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"

	mcp "github.com/metoro-io/mcp-golang"
)

const RDW_API_ENDPOINT = "https://opendata.rdw.nl/resource/m9d7-ebf2.json"
const RDW_AXLES_API_ENDPOINT = "https://opendata.rdw.nl/resource/3huj-srit.json"

type VehicleArgs struct {
	Kenteken string `json:"kenteken" jsonschema:"description=Het kenteken van het voertuig (bijv. 41TDK8 of 41-TDK-8)."`
}

func main() {
	s := mcp.NewServer("rdw-server-go", "1.2.4")

	if err := s.RegisterTool("get_vehicle_info", "Haal gedetailleerde technische informatie op over een Nederlands voertuig op basis van het kenteken.", func(args VehicleArgs) (string, error) {
		kenteken := strings.ToUpper(strings.ReplaceAll(args.Kenteken, "-", ""))
		kenteken = strings.ReplaceAll(kenteken, " ", "")

		resp, err := http.Get(fmt.Sprintf("%s?kenteken=%s", RDW_API_ENDPOINT, kenteken))
		if err != nil {
			return "", fmt.Errorf("fout bij verbinden met RDW API: %w", err)
		}
		defer resp.Body.Close()

		if resp.StatusCode != http.StatusOK {
			return "", fmt.Errorf("RDW API fout: %s", resp.Status)
		}

		body, err := io.ReadAll(resp.Body)
		if err != nil {
			return "", fmt.Errorf("fout bij lezen van RDW API response: %w", err)
		}

		var data []map[string]interface{}
		if err := json.Unmarshal(body, &data); err != nil {
			return "", fmt.Errorf("fout bij parsen van JSON: %w", err)
		}

		if len(data) == 0 {
			return fmt.Sprintf("Geen voertuig gevonden voor kenteken: %s", kenteken), nil
		}

		prettyJSON, _ := json.MarshalIndent(data[0], "", "  ")
		return string(prettyJSON), nil
	}); err != nil {
		panic(err)
	}

	if err := s.RegisterTool("get_vehicle_axles", "Haal informatie op over de assen van een voertuig op basis van het kenteken.", func(args VehicleArgs) (string, error) {
		kenteken := strings.ToUpper(strings.ReplaceAll(args.Kenteken, "-", ""))
		kenteken = strings.ReplaceAll(kenteken, " ", "")

		resp, err := http.Get(fmt.Sprintf("%s?kenteken=%s", RDW_AXLES_API_ENDPOINT, kenteken))
		if err != nil {
			return "", fmt.Errorf("fout bij verbinden met RDW API: %w", err)
		}
		defer resp.Body.Close()

		if resp.StatusCode != http.StatusOK {
			return "", fmt.Errorf("RDW API fout: %s", resp.Status)
		}

		body, err := io.ReadAll(resp.Body)
		if err != nil {
			return "", fmt.Errorf("fout bij lezen van RDW API response: %w", err)
		}

		var data []map[string]interface{}
		if err := json.Unmarshal(body, &data); err != nil {
			return "", fmt.Errorf("fout bij parsen van JSON: %w", err)
		}

		if len(data) == 0 {
			return fmt.Sprintf("Geen as-informatie gevonden voor kenteken: %s. Let op: lichte personenauto's hebben vaak geen vermelding in deze dataset.", kenteken), nil
		}

		prettyJSON, _ := json.MarshalIndent(data, "", "  ")
		return string(prettyJSON), nil
	}); err != nil {
		panic(err)
	}

	if err := s.ServeStdio(); err != nil {
		panic(err)
	}
}
