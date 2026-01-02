<?php
/**
 * RDW Vehicle Info MCP Server (PHP)
 * Authors: Dirk-Jan Berman & Gemini 3
 * License: MIT
 */

require __DIR__ . '/vendor/autoload.php';

use GuzzleHttp\Client;

const RDW_API_ENDPOINT = "https://opendata.rdw.nl/resource/m9d7-ebf2.json";
$client = new Client();

while ($line = fgets(STDIN)) {
    $request = json_decode($line, true);
    if (!$request) continue;

    $method = $request['method'] ?? '';
    $id = $request['id'] ?? null;

    if ($method === 'list_tools') {
        $response = [
            'jsonrpc' => '2.0',
            'id' => $id,
            'result' => [
                'tools' => [
                    [
                        'name' => 'get_vehicle_info',
                        'description' => 'Haal gedetailleerde technische informatie op over een Nederlands voertuig op basis van het kenteken.',
                        'inputSchema' => [
                            'type' => 'object',
                            'properties' => [
                                'kenteken' => ['type' => 'string', 'description' => "Het kenteken van het voertuig (bijv. '41TDK8')."]
                            ],
                            'required' => ['kenteken']
                        ]
                    ]
                ]
            ]
        ];
        echo json_encode($response) . PHP_EOL;
    } elseif ($method === 'call_tool' && ($request['params']['name'] ?? '') === 'get_vehicle_info') {
        $kenteken = $request['params']['arguments']['kenteken'] ?? '';
        $cleanKenteken = str_replace(['-', ' '], '', strtoupper($kenteken));

        try {
            $res = $client->request('GET', RDW_API_ENDPOINT, [
                'query' => ['kenteken' => $cleanKenteken],
                'timeout' => 10
            ]);
            $data = json_decode($res->getBody(), true);

            if (empty($data)) {
                $content = "Geen voertuig gevonden voor kenteken: $cleanKenteken";
            } else {
                $content = json_encode($data[0], JSON_PRETTY_PRINT);
            }
        } catch (\Exception $e) {
            $content = "Fout bij ophalen RDW data: " . $e->getMessage();
        }

        $response = [
            'jsonrpc' => '2.0',
            'id' => $id,
            'result' => [
                'content' => [
                    ['type' => 'text', 'text' => $content]
                ]
            ]
        ];
        echo json_encode($response) . PHP_EOL;
    }
}
