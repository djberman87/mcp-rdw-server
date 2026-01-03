/**
 * RDW Vehicle Info MCP Server (.NET)
 * Authors: Dirk-Jan Berman & Gemini 3
 * Version: 2.0.0
 * License: MIT
 */
using System;
using System.Net.Http;
using System.Text.Json;
using System.Threading.Tasks;
using System.Collections.Generic;
using System.Linq;

namespace RDWMcpServer;

class Program
{
    private static readonly HttpClient client = new HttpClient();
    private static readonly Dictionary<string, string> ENDPOINTS = new()
    {
        { "info", "https://opendata.rdw.nl/resource/m9d7-ebf2.json" },
        { "odometer", "https://opendata.rdw.nl/resource/v3i9-dpe8.json" },
        { "fuel", "https://opendata.rdw.nl/resource/8ys7-d773.json" },
        { "axles", "https://opendata.rdw.nl/resource/3huj-srit.json" },
        { "remarks", "https://opendata.rdw.nl/resource/7ug8-2dtt.json" },
        { "subcategory", "https://opendata.rdw.nl/resource/wj78-6f6f.json" },
        { "tracks", "https://opendata.rdw.nl/resource/p693-vshn.json" },
        { "bodywork", "https://opendata.rdw.nl/resource/vezc-m2t6.json" },
        { "bodywork_specific", "https://opendata.rdw.nl/resource/jhie-znh9.json" },
        { "vehicle_class", "https://opendata.rdw.nl/resource/kmfi-hrps.json" }
    };

    static string NormalizeKenteken(string kenteken) => kenteken.ToUpper().Replace("-", "").Replace(" ", "");

    static async Task<JsonElement> FetchRdwData(string endpoint, string kenteken)
    {
        try
        {
            var response = await client.GetAsync($"{endpoint}?kenteken={kenteken}");
            var body = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<JsonElement>(body);
        }
        catch { return default; }
    }

    static async Task Main(string[] args)
    {
        string? line;
        while ((line = Console.ReadLine()) != null)
        {
            try 
            {
                using var doc = JsonDocument.Parse(line);
                var root = doc.RootElement;
                var method = root.GetProperty("method").GetString();
                var id = root.GetProperty("id");

                if (method == "initialize")
                {
                    var response = new {
                        jsonrpc = "2.0",
                        id = id,
                        result = new {
                            protocolVersion = "2024-11-05",
                            capabilities = new { tools = new { } },
                            serverInfo = new { name = "rdw-server-dotnet", version = "2.0.0" }
                        }
                    };
                    Console.WriteLine(JsonSerializer.Serialize(response));
                }
                else if (method == "list_tools")
                {
                    var response = new
                    {
                        jsonrpc = "2.0",
                        id = id,
                        result = new
                        {
                            tools = new[]
                            {
                                new { name = "get_vehicle_info", description = "Haal algemene voertuiggegevens op (Merk, Model, APK, etc.). Dataset: m9d7-ebf2" },
                                new { name = "get_odometer_judgment", description = "Decodeert tellerstand-codes naar tekstuele uitleg (logisch/onlogisch). Dataset: v3i9-dpe8" },
                                new { name = "get_vehicle_fuel", description = "Brandstofverbruik en emissiegegevens. Dataset: 8ys7-d773" },
                                new { name = "get_vehicle_axles", description = "Informatie over de assen van een voertuig (aslasten, aantal assen). Dataset: 3huj-srit" },
                                new { name = "get_vehicle_remarks", description = "Bijzonderheden en specifieke registraties (bijv. taxi, ambulance). Dataset: 7ug8-2dtt" },
                                new { name = "get_vehicle_subcategory", description = "Specifieke voertuig-subcategorie. Dataset: wj78-6f6f" },
                                new { name = "get_vehicle_tracks", description = "Informatie over rupsband-sets. Dataset: p693-vshn" },
                                new { name = "get_vehicle_bodywork", description = "Gecombineerde carrosseriegegevens uit meerdere RDW datasets. Datasets: vezc-m2t6, jhie-znh9, kmfi-hrps" }
                            }
                        }
                    };
                    Console.WriteLine(JsonSerializer.Serialize(response));
                }
                else if (method == "call_tool")
                {
                    var toolName = root.GetProperty("params").GetProperty("name").GetString();
                    var kenteken = NormalizeKenteken(root.GetProperty("params").GetProperty("arguments").GetProperty("kenteken").GetString() ?? "");

                    string content;
                    if (toolName == "get_vehicle_bodywork")
                    {
                        var bTask = FetchRdwData(ENDPOINTS["bodywork"], kenteken);
                        var sTask = FetchRdwData(ENDPOINTS["bodywork_specific"], kenteken);
                        var cTask = FetchRdwData(ENDPOINTS["vehicle_class"], kenteken);
                        await Task.WhenAll(bTask, sTask, cTask);

                        var combined = new {
                            kenteken,
                            carrosserie = bTask.Result,
                            carrosserie_specifiek = sTask.Result,
                            voertuigklasse = cTask.Result
                        };
                        
                        bool hasData = (bTask.Result.ValueKind == JsonValueKind.Array && bTask.Result.GetArrayLength() > 0) ||
                                       (sTask.Result.ValueKind == JsonValueKind.Array && sTask.Result.GetArrayLength() > 0) ||
                                       (cTask.Result.ValueKind == JsonValueKind.Array && cTask.Result.GetArrayLength() > 0);

                        content = hasData ? JsonSerializer.Serialize(combined, new JsonSerializerOptions { WriteIndented = true })
                                          : $"Geen carrosseriegegevens gevonden voor kenteken: {kenteken}";
                    }
                    else
                    {
                        var endpointMap = new Dictionary<string, string> {
                            { "get_vehicle_info", ENDPOINTS["info"] },
                            { "get_odometer_judgment", ENDPOINTS["odometer"] },
                            { "get_vehicle_fuel", ENDPOINTS["fuel"] },
                            { "get_vehicle_axles", ENDPOINTS["axles"] },
                            { "get_vehicle_remarks", ENDPOINTS["remarks"] },
                            { "get_vehicle_subcategory", ENDPOINTS["subcategory"] },
                            { "get_vehicle_tracks", ENDPOINTS["tracks"] }
                        };

                        if (endpointMap.TryGetValue(toolName!, out var endpoint))
                        {
                            var data = await FetchRdwData(endpoint, kenteken);
                            if (data.ValueKind == JsonValueKind.Array && data.GetArrayLength() > 0)
                            {
                                var result = (toolName == "get_vehicle_info" || toolName == "get_odometer_judgment") ? data[0] : data;
                                content = JsonSerializer.Serialize(result, new JsonSerializerOptions { WriteIndented = true });
                            }
                            else
                            {
                                content = $"Geen gegevens gevonden voor kenteken: {kenteken}";
                            }
                        }
                        else { content = "Tool niet gevonden"; }
                    }

                    var response = new {
                        jsonrpc = "2.0",
                        id = id,
                        result = new {
                            content = new[] { new { type = "text", text = content } }
                        }
                    };
                    Console.WriteLine(JsonSerializer.Serialize(response));
                }
            }
            catch (Exception ex) { Console.Error.WriteLine($"Error: {ex.Message}"); }
        }
    }
}
