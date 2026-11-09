Based on https://github.com/espressif/esp32-camera/

Built using ESP-IDF using example from above repository (in examples/camera_example) in vscode extension

Built for ESP32S3 WROOM using OV7670.

Need to generate vscode configuration with command "ESP-IDF: Add VS Code configuration folder". Generated c_cpp_properties.json required additional configuration (at least on my system), add following:
```
"configurations":[{

...,

"compileCommands":"<PATH/TO/THIS/build/compile_commands.json>"

}]
```
local_vars.h not in repository for practical reason, it defines wifi SSID and password as follows:
```
#define ESP_WIFI_SSID "ssid_name"
#define ESP_WIFI_PASS "password"
```
