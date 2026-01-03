/**
 * RDW Vehicle Info MCP Server (Java)
 * Authors: Dirk-Jan Berman & Gemini 3
 * Version: 2.0.0
 * License: MIT
 */
package com.rdw;

import com.google.gson.*;
import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.HashMap;
import java.util.Map;
import java.util.Scanner;

public class McpServer {
    private static final Map<String, String> ENDPOINTS = new HashMap<>();
    static {
        ENDPOINTS.put("info", "https://opendata.rdw.nl/resource/m9d7-ebf2.json");
        ENDPOINTS.put("odometer", "https://opendata.rdw.nl/resource/v3i9-dpe8.json");
        ENDPOINTS.put("fuel", "https://opendata.rdw.nl/resource/8ys7-d773.json");
        ENDPOINTS.put("axles", "https://opendata.rdw.nl/resource/3huj-srit.json");
        ENDPOINTS.put("remarks", "https://opendata.rdw.nl/resource/7ug8-2dtt.json");
        ENDPOINTS.put("subcategory", "https://opendata.rdw.nl/resource/wj78-6f6f.json");
        ENDPOINTS.put("tracks", "https://opendata.rdw.nl/resource/p693-vshn.json");
        ENDPOINTS.put("bodywork", "https://opendata.rdw.nl/resource/vezc-m2t6.json");
        ENDPOINTS.put("bodywork_specific", "https://opendata.rdw.nl/resource/jhie-znh9.json");
        ENDPOINTS.put("vehicle_class", "https://opendata.rdw.nl/resource/kmfi-hrps.json");
    }
    
    private static final Gson gson = new GsonBuilder().setPrettyPrinting().create();

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        while (scanner.hasNextLine()) {
            String line = scanner.nextLine();
            try {
                JsonObject request = JsonParser.parseString(line).getAsJsonObject();
                String method = request.get("method").getAsString();
                JsonElement id = request.get("id");

                if ("initialize".equals(method)) {
                    JsonObject result = new JsonObject();
                    result.addProperty("protocolVersion", "2024-11-05");
                    result.add("capabilities", new JsonObject());
                    JsonObject serverInfo = new JsonObject();
                    serverInfo.addProperty("name", "rdw-server-java");
                    serverInfo.addProperty("version", "2.0.0");
                    result.add("serverInfo", serverInfo);
                    sendResponse(id, result);
                } else if ("list_tools".equals(method)) {
                    sendResponse(id, createListToolsResult());
                } else if ("call_tool".equals(method)) {
                    String toolName = request.get("params").getAsJsonObject().get("name").getAsString();
                    String kenteken = request.get("params").getAsJsonObject()
                            .get("arguments").getAsJsonObject()
                            .get("kenteken").getAsString();
                    handleCallTool(id, toolName, kenteken);
                }
            } catch (Exception e) {}
        }
    }

    private static String normalizeKenteken(String kenteken) {
        return kenteken.toUpperCase().replace("-", "").replace(" ", "");
    }

    private static JsonArray fetchRdwData(String endpoint, String kenteken) {
        try {
            URL url = new URL(endpoint + "?kenteken=" + kenteken);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("GET");
            InputStream is = conn.getInputStream();
            Scanner s = new Scanner(is).useDelimiter("\\A");
            String result = s.hasNext() ? s.next() : "[]";
            return JsonParser.parseString(result).getAsJsonArray();
        } catch (Exception e) {
            return new JsonArray();
        }
    }

    private static void handleCallTool(JsonElement id, String toolName, String kenteken) throws Exception {
        String cleanKenteken = normalizeKenteken(kenteken);
        String content;

        if ("get_vehicle_bodywork".equals(toolName)) {
            JsonArray bodywork = fetchRdwData(ENDPOINTS.get("bodywork"), cleanKenteken);
            JsonArray specific = fetchRdwData(ENDPOINTS.get("bodywork_specific"), cleanKenteken);
            JsonArray vehicleClass = fetchRdwData(ENDPOINTS.get("vehicle_class"), cleanKenteken);

            JsonObject combined = new JsonObject();
            combined.addProperty("kenteken", cleanKenteken);
            combined.add("carrosserie", bodywork);
            combined.add("carrosserie_specifiek", specific);
            combined.add("voertuigklasse", vehicleClass);

            if (bodywork.size() == 0 && specific.size() == 0 && vehicleClass.size() == 0) {
                content = "Geen carrosseriegegevens gevonden voor kenteken: " + cleanKenteken;
            } else {
                content = gson.toJson(combined);
            }
        } else {
            Map<String, String> map = new HashMap<>();
            map.put("get_vehicle_info", ENDPOINTS.get("info"));
            map.put("get_odometer_judgment", ENDPOINTS.get("odometer"));
            map.put("get_vehicle_fuel", ENDPOINTS.get("fuel"));
            map.put("get_vehicle_axles", ENDPOINTS.get("axles"));
            map.put("get_vehicle_remarks", ENDPOINTS.get("remarks"));
            map.put("get_vehicle_subcategory", ENDPOINTS.get("subcategory"));
            map.put("get_vehicle_tracks", ENDPOINTS.get("tracks"));

            String endpoint = map.get(toolName);
            if (endpoint == null) {
                content = "Tool niet gevonden";
            } else {
                JsonArray data = fetchRdwData(endpoint, cleanKenteken);
                if (data.size() == 0) {
                    content = "Geen gegevens gevonden voor kenteken: " + cleanKenteken;
                } else {
                    JsonElement result = ("get_vehicle_info".equals(toolName) || "get_odometer_judgment".equals(toolName)) ? data.get(0) : data;
                    content = gson.toJson(result);
                }
            }
        }

        JsonObject responseResult = new JsonObject();
        JsonArray contentArray = new JsonArray();
        JsonObject textObj = new JsonObject();
        textObj.addProperty("type", "text");
        textObj.addProperty("text", content);
        contentArray.add(textObj);
        responseResult.add("content", contentArray);
        sendResponse(id, responseResult);
    }

    private static JsonObject createListToolsResult() {
        JsonObject result = new JsonObject();
        JsonArray tools = new JsonArray();
        tools.add(createToolObject("get_vehicle_info", "Haal algemene voertuiggegevens op (Merk, Model, APK, etc.). Dataset: m9d7-ebf2"));
        tools.add(createToolObject("get_odometer_judgment", "Decodeert tellerstand-codes naar tekstuele uitleg (logisch/onlogisch). Dataset: v3i9-dpe8"));
        tools.add(createToolObject("get_vehicle_fuel", "Brandstofverbruik en emissiegegevens. Dataset: 8ys7-d773"));
        tools.add(createToolObject("get_vehicle_axles", "Informatie over de assen van een voertuig (aslasten, aantal assen). Dataset: 3huj-srit"));
        tools.add(createToolObject("get_vehicle_remarks", "Bijzonderheden en specifieke registraties (bijv. taxi, ambulance). Dataset: 7ug8-2dtt"));
        tools.add(createToolObject("get_vehicle_subcategory", "Specifieke voertuig-subcategorie. Dataset: wj78-6f6f"));
        tools.add(createToolObject("get_vehicle_tracks", "Informatie over rupsband-sets. Dataset: p693-vshn"));
        tools.add(createToolObject("get_vehicle_bodywork", "Gecombineerde carrosseriegegevens uit meerdere RDW datasets. Datasets: vezc-m2t6, jhie-znh9, kmfi-hrps"));
        result.add("tools", tools);
        return result;
    }

    private static JsonObject createToolObject(String name, String description) {
        JsonObject tool = new JsonObject();
        tool.addProperty("name", name);
        tool.addProperty("description", description);
        JsonObject schema = new JsonObject();
        schema.addProperty("type", "object");
        JsonObject props = new JsonObject();
        JsonObject kentekenProp = new JsonObject();
        kentekenProp.addProperty("type", "string");
        kentekenProp.addProperty("description", "Het Nederlandse kenteken.");
        props.add("kenteken", kentekenProp);
        schema.add("properties", props);
        JsonArray required = new JsonArray();
        required.add("kenteken");
        schema.add("required", required);
        tool.add("inputSchema", schema);
        return tool;
    }

    private static void sendResponse(JsonElement id, JsonObject result) {
        JsonObject response = new JsonObject();
        response.addProperty("jsonrpc", "2.0");
        response.add("id", id != null && !id.isJsonNull() ? id : null);
        response.add("result", result);
        System.out.println(new Gson().toJson(response));
    }
}
