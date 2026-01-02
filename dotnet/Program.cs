/**
 * RDW Vehicle Info MCP Server (.NET)
 * Authors: Dirk-Jan Berman & Gemini 3
 * License: MIT
 */
using System;
using System.Net.Http;
using System.Text.Json;
using System.Threading.Tasks;
using System.Collections.Generic;

namespace RDWMcpServer;

class Program
{
    private static readonly HttpClient client = new HttpClient();
    private const string RDW_API_ENDPOINT = "https://opendata.rdw.nl/resource/m9d7-ebf2.json";
    private const string RDW_AXLES_API_ENDPOINT = "https://opendata.rdw.nl/resource/3huj-srit.json";

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

                if (method == "list_tools")
                {
                    var response = new
                    {
                        jsonrpc = "2.0",
                        id = id,
                        result = new
                        {
                            tools = new[]
                            {
                                new
                                {
                                    name = "get_vehicle_info",
                                    description = "Haal gedetailleerde technische informatie op over een Nederlands voertuig op basis van het kenteken.",
                                    inputSchema = new
                                    {
                                        type = "object",
                                        properties = new
                                        {
                                            kenteken = new { type = "string", description = "Het kenteken van het voertuig (bijv. '41TDK8')." }
                                        },
                                        required = new[] { "kenteken" }
                                    }
                                },
                                new
                                {
                                    name = "get_vehicle_axles",
                                    description = "Haal informatie op over de assen van een voertuig op basis van het kenteken.",
                                    inputSchema = new
                                    {
                                        type = "object",
                                        properties = new
                                        {
                                            kenteken = new { type = "string", description = "Het kenteken van het voertuig (bijv. '41TDK8')." }
                                        },
                                        required = new[] { "kenteken" }
                                    }
                                }
                            }
                        }
                    };
                    Console.WriteLine(JsonSerializer.Serialize(response));
                }
                else if (method == "call_tool")
                {
                    var toolName = root.GetProperty("params").GetProperty("name").GetString();
                    var kenteken = root.GetProperty("params").GetProperty("arguments").GetProperty("kenteken").GetString() ?? "";
                    kenteken = kenteken.ToUpper().Replace("-", "").Replace(" ", "");

                    string apiUrl = toolName switch {
                        "get_vehicle_info" => $"{RDW_API_ENDPOINT}?kenteken={kenteken}",
                        "get_vehicle_axles" => $"{RDW_AXLES_API_ENDPOINT}?kenteken={kenteken}",
                        _ => ""
                    };

                    if (string.IsNullOrEmpty(apiUrl)) continue;

                    var httpResponse = await client.GetAsync(apiUrl);
                    var body = await httpResponse.Content.ReadAsStringAsync();
                    var data = JsonSerializer.Deserialize<JsonElement>(body);

                    string content;
                    if (data.ValueKind == JsonValueKind.Array && data.GetArrayLength() > 0)
                    {
                        content = toolName == "get_vehicle_info" 
                            ? JsonSerializer.Serialize(data[0], new JsonSerializerOptions { WriteIndented = true })
                            : JsonSerializer.Serialize(data, new JsonSerializerOptions { WriteIndented = true });
                    }
                    else
                    {
                        content = toolName == "get_vehicle_info"
                            ? $"Geen voertuig gevonden voor kenteken: {kenteken}"
                            : $"Geen as-informatie gevonden voor kenteken: {kenteken}. Let op: lichte personenauto's hebben vaak geen vermelding in deze dataset.";
                    }

                    var response = new
                    {
                        jsonrpc = "2.0",
                        id = id,
                        result = new
                        {
                            content = new[]
                            {
                                new { type = "text", text = content }
                            }
                        }
                    };
                    Console.WriteLine(JsonSerializer.Serialize(response));
                }
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine($"Error: {ex.Message}");
            }
        }
    }
}
