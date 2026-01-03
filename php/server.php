<?php
/**
 * RDW Vehicle Info MCP Server (PHP)
 * Authors: Dirk-Jan Berman & Gemini 3
 * Version: 2.0.0
 * License: MIT
 */

require __DIR__ . '/vendor/autoload.php';

use GuzzleHttp\Client;

const ENDPOINTS = [
    "info" => "https://opendata.rdw.nl/resource/m9d7-ebf2.json",
    "odometer" => "https://opendata.rdw.nl/resource/v3i9-dpe8.json",
    "fuel" => "https://opendata.rdw.nl/resource/8ys7-d773.json",
    "axles" => "https://opendata.rdw.nl/resource/3huj-srit.json",
    "remarks" => "https://opendata.rdw.nl/resource/7ug8-2dtt.json",
    "subcategory" => "https://opendata.rdw.nl/resource/wj78-6f6f.json",
    "tracks" => "https://opendata.rdw.nl/resource/p693-vshn.json",
    "bodywork" => "https://opendata.rdw.nl/resource/vezc-m2t6.json",
    "bodywork_specific" => "https://opendata.rdw.nl/resource/jhie-znh9.json",
    "vehicle_class" => "https://opendata.rdw.nl/resource/kmfi-hrps.json"
];

$client = new Client();

function normalizeKenteken($kenteken) {
    return str_replace(['-', ' '], '', strtoupper($kenteken));
}

function fetchRdwData($client, $endpoint, $kenteken) {
    try {
        $res = $client->request('GET', $endpoint, [
            'query' => ['kenteken' => $kenteken],
            'timeout' => 10
        ]);
        return json_decode($res->getBody(), true);
    } catch (\Exception $e) {
        return [];
    }
}

while ($line = fgets(STDIN)) {
    $request = json_decode($line, true);
    if (!$request) continue;

    $method = $request['method'] ?? '';
    $id = $request['id'] ?? null;

    if ($method === 'initialize') {
        $response = [
            'jsonrpc' => '2.0',
            'id' => $id,
            'result' => [
                'protocolVersion' => '2024-11-05',
                'capabilities' => ['tools' => []],
                'serverInfo' => ['name' => 'rdw-server-php', 'version' => '2.0.0']
            ]
        ];
        echo json_encode($response) . PHP_EOL;
    } elseif ($method === 'list_tools') {
        $response = [
            'jsonrpc' => '2.0',
            'id' => $id,
            'result' => [
                'tools' => [
                    ['name' => 'get_vehicle_info', 'description' => 'Haal algemene voertuiggegevens op (Merk, Model, APK, etc.). Dataset: m9d7-ebf2'],
                    ['name' => 'get_odometer_judgment', 'description' => 'Decodeert tellerstand-codes naar tekstuele uitleg (logisch/onlogisch). Dataset: v3i9-dpe8'],
                    ['name' => 'get_vehicle_fuel', 'description' => 'Brandstofverbruik en emissiegegevens. Dataset: 8ys7-d773'],
                    ['name' => 'get_vehicle_axles', 'description' => 'Informatie over de assen van een voertuig (aslasten, aantal assen). Dataset: 3huj-srit'],
                    ['name' => 'get_vehicle_remarks', 'description' => 'Bijzonderheden en specifieke registraties (bijv. taxi, ambulance). Dataset: 7ug8-2dtt'],
                    ['name' => 'get_vehicle_subcategory', 'description' => 'Specifieke voertuig-subcategorie. Dataset: wj78-6f6f'],
                    ['name' => 'get_vehicle_tracks', 'description' => 'Informatie over rupsband-sets. Dataset: p693-vshn'],
                    ['name' => 'get_vehicle_bodywork', 'description' => 'Gecombineerde carrosseriegegevens uit meerdere RDW datasets. Datasets: vezc-m2t6, jhie-znh9, kmfi-hrps']
                ]
            ]
        ];
        echo json_encode($response) . PHP_EOL;
    } elseif ($method === 'call_tool') {
        $toolName = $request['params']['name'] ?? '';
        $kenteken = normalizeKenteken($request['params']['arguments']['kenteken'] ?? '');
        $content = "";

        if ($toolName === 'get_vehicle_bodywork') {
            $b = fetchRdwData($client, ENDPOINTS['bodywork'], $kenteken);
            $s = fetchRdwData($client, ENDPOINTS['bodywork_specific'], $kenteken);
            $c = fetchRdwData($client, ENDPOINTS['vehicle_class'], $kenteken);
            
            if (empty($b) && empty($s) && empty($c)) {
                $content = "Geen carrosseriegegevens gevonden voor kenteken: $kenteken";
            } else {
                $content = json_encode([
                    'kenteken' => $kenteken,
                    'carrosserie' => $b,
                    'carrosserie_specifiek' => $s,
                    'voertuigklasse' => $c
                ], JSON_PRETTY_PRINT);
            }
        } else {
            $map = [
                'get_vehicle_info' => ENDPOINTS['info'],
                'get_odometer_judgment' => ENDPOINTS['odometer'],
                'get_vehicle_fuel' => ENDPOINTS['fuel'],
                'get_vehicle_axles' => ENDPOINTS['axles'],
                'get_vehicle_remarks' => ENDPOINTS['remarks'],
                'get_vehicle_subcategory' => ENDPOINTS['subcategory'],
                'get_vehicle_tracks' => ENDPOINTS['tracks']
            ];

            if (isset($map[$toolName])) {
                $data = fetchRdwData($client, $map[$toolName], $kenteken);
                if (empty($data)) {
                    $content = "Geen gegevens gevonden voor kenteken: $kenteken";
                } else {
                    $result = ($toolName === 'get_vehicle_info' || $toolName === 'get_odometer_judgment') ? $data[0] : $data;
                    $content = json_encode($result, JSON_PRETTY_PRINT);
                }
            } else {
                $content = "Tool niet gevonden";
            }
        }

        $response = [
            'jsonrpc' => '2.0',
            'id' => $id,
            'result' => [
                'content' => [['type' => 'text', 'text' => $content]]
            ]
        ];
        echo json_encode($response) . PHP_EOL;
    }
}
