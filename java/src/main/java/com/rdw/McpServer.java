/**
 * RDW Vehicle Info MCP Server (Java)
 * Authors: Dirk-Jan Berman & Gemini 3
 * License: MIT
 */
package com.rdw;

import com.google.gson.*;
import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Scanner;

public class McpServer {
    private static final String RDW_API_ENDPOINT = "https://opendata.rdw.nl/resource/m9d7-ebf2.json";
    private static final Gson gson = new GsonBuilder().setPrettyPrinting().create();

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        while (scanner.hasNextLine()) {
            String line = scanner.nextLine();
            try {
                JsonObject request = JsonParser.parseString(line).getAsJsonObject();
                String method = request.get("method").getAsString();
                JsonElement id = request.get("id");

                if ("list_tools".equals(method)) {
                    sendResponse(id, createListToolsResult());
                } else if ("call_tool".equals(method)) {
                    String toolName = request.get("params").getAsJsonObject().get("name").getAsString();
                    if ("get_vehicle_info".equals(toolName)) {
                        String kenteken = request.get("params").getAsJsonObject()
                                .get("arguments").getAsJsonObject()
                                .get("kenteken").getAsString();
                        handleGetVehicleInfo(id, kenteken);
                    }
                }
            } catch (Exception e) {
                // Ignore errors for simple stdio implementation
            }
        }
    }

    private static void handleGetVehicleInfo(JsonElement id, String kenteken) throws Exception {
        String cleanKenteken = kenteken.toUpperCase().replace("-", "").replace(" ", "");
        URL url = new URL(RDW_API_ENDPOINT + "?kenteken=" + cleanKenteken);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("GET");

        Scanner s = new Scanner(conn.getInputStream()).useDelimiter("\\A");
        String result = s.hasNext() ? s.next() : "[]";
        JsonArray data = JsonParser.parseString(result).getAsJsonArray();

        String content;
        if (data.size() > 0) {
            content = gson.toJson(data.get(0));
        } else {
            content = "Geen voertuig gevonden voor kenteken: " + cleanKenteken;
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
        JsonObject tool = new JsonObject();
        tool.addProperty("name", "get_vehicle_info");
        tool.addProperty("description", "Haal gedetailleerde technische informatie op over een Nederlands voertuig op basis van het kenteken.");
        
        JsonObject schema = new JsonObject();
        schema.addProperty("type", "object");
        JsonObject props = new JsonObject();
        JsonObject kentekenProp = new JsonObject();
        kentekenProp.addProperty("type", "string");
        kentekenProp.addProperty("description", "Het kenteken van het voertuig (bijv. '41TDK8').");
        props.add("kenteken", kentekenProp);
        schema.add("properties", props);
        JsonArray required = new JsonArray();
        required.add("kenteken");
        schema.add("required", required);
        
        tool.add("inputSchema", schema);
        tools.add(tool);
        result.add("tools", tools);
        return result;
    }

    private static void sendResponse(JsonElement id, JsonObject result) {
        JsonObject response = new JsonObject();
        response.addProperty("jsonrpc", "2.0");
        response.add("id", id != null && !id.isJsonNull() ? id.getAsLong() : null);
        response.add("result", result);
        System.out.println(new Gson().toJson(response));
    }
}
