
const { spawn } = require('child_process');

async function testNodeExtension() {
  console.log("Testing Node.js extension tool: get_vehicle_axles");
  
  const server = spawn('node', ['/home/djberman/.gemini/extensions/rdw/index.js']);
  
  const listToolsRequest = JSON.stringify({
    jsonrpc: "2.0",
    id: 1,
    method: "list_tools",
    params: {}
  }) + "\n";

  const callToolRequest = JSON.stringify({
    jsonrpc: "2.0",
    id: 2,
    method: "call_tool",
    params: {
      name: "get_vehicle_axles",
      arguments: { kenteken: "BB943Z" }
    }
  }) + "\n";

  server.stdin.write(listToolsRequest);
  
  server.stdout.on('data', (data) => {
    const response = JSON.parse(data.toString());
    console.log(`Response ID ${response.id}:`, JSON.stringify(response, null, 2));
    if (response.id === 1) {
      server.stdin.write(callToolRequest);
    } else if (response.id === 2) {
      server.kill();
      process.exit(0);
    }
  });

  server.stderr.on('data', (data) => {
    console.error(`Stderr: ${data}`);
  });
}

testNodeExtension();
