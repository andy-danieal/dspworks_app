"""Constants for the DSPWorks Automation Devices integration."""

DOMAIN = "dspworks_app"
DOMAIN_IP = "https://do1.dspworks.in"
DOMAIN_API_URL="/api/bldc/index.php"
DOMAIN_URL = "https://do1.dspworks.in/api/bldc/index.php"

OAUTH_CLIENT_ID = "VAYU-HOME-DSP"
OAUTH_CLIENT_SECRET = "DSP@HOME@VAYU"
OAUTH_LOGIN_URL = "/Oauth2/Login/index"
OAUTH_TOKEN_URL = "/Oauth2/Login/token"
DSPWORKS_SCOPES = ['cloud']

DISCOVERY_DEVICES = "/api/VayuAssistant/discovery"
GET_DEVICE = "/api/VayuAssistant/state"
DEVICE_SET = "/api/VayuAssistant/control"

SERVICE_SET_FAN_SPEED_TRACKED_STATE = "set_fan_speed_tracked_state"
SERVICE_SET_POWER_TRACKED_STATE = "set_switch_power_tracked_state"
SERVICE_SET_LIGHT_POWER_TRACKED_STATE = "set_light_power_tracked_state"
SERVICE_SET_LIGHT_BRIGHTNESS_TRACKED_STATE = "set_light_brightness_tracked_state"
ATTR_POWER_STATE = "power_state"
