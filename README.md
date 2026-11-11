Based on https://github.com/espressif/esp32-camera/

Built using ESP-IDF (and vscode extension), example from above repository (in examples/camera_example)

Targeting ESP32S3 WROOM with OV7670.

Need to generate vscode configuration with command "ESP-IDF: Add VS Code configuration folder". Generated c_cpp_properties.json required additional configuration (at least on my system), add following:
```
"configurations":[{

...,

"compileCommands":"PATH/TO/THIS/build/compile_commands.json"

}]
```
local_vars.h not in repository for practical reason, it defines wifi SSID and password as follows:
```
#define ESP_WIFI_AP_SSID "ssid_ap_name"
#define ESP_WIFI_AP_PASS "password"
#define ESP_WIFI_STA_SSID "ssid_of_ap_to_connect"
#define ESP_WIFI_STA_PASS "password_to_ap_connect"
```
