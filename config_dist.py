# General config
is_metric = 1 # 0 for metric or 1 for imperial
sync_weather = 1 # whether o sync with HA to get and display weather data
show_seconds = 1 # whether to show seconds (1) or no (0)
use_24h_clock = 1 # if use (1) the 24-hours clock or not - show AM/PM. If sset to 0 and sync_weather is set to one, seconds will be hidden. Unless disable_ampm is set to 1.
disable_ampm = 0 # if set to 1 then do not show AM/PM even in the non-24hrs mode

# Wifi connection settings config
wifi_ip_config = {'mode':'static', 'params':{'ip':'192.168.0.10','mask':'255.255.255.0','gateway':'192.168.0.1','dns':'192.168.0.1'}} # mode can be either static or dhcp. When set to DHCP 'params' are ignored.

#NTP config
ntp_host = ["0.pool.ntp.org","1.pool.ntp.org"] # array of NTP hosts in order of attempt to sync
daylight_time_savings = 1 # whether to disable (0) or enable (1) daylight time savings
resync_ntp = 1 # whether to re-sync with NTP server after synced once on load
resync_ntp_frequency_sec = 604800 # How often to re-sync with NTP server - e.g. once in 86400*7 - 7 days
reconnect_on_ntp_gone = 0 # 0 for skip sync with NTP server if failed to re-sync or 1 for re-connect to WiFi and sync again (basically to re-start board). Will do so until the sync finally happens.
ntp_srv_timeout = 20 # how long to wait for the NTP server to respond. In seconds.
time_shift_minutes = 60 # time shift 

#HA config
reconnect_on_ha_gone = 1 # re-connect to WiFi if the HA server is gone. Will do that until the server becomes available.
ha_srv_timeout = 20  # how long to wait for the HA server to respond. In seconds.
ha_api_url_temperature = "https://homeassistant.myawesomeserver:8123/api/states/weather.forecast_dom" # HA API url.
ha_api_temperature_json_path = "['attributes']['temperature']" # the json sctructure to get the temperature from
temperature_units = "celsius" # set the display to celsius, kelvin or farenheit. It doesn't convert data, just displays the symbol. If it is set to anything else - displays no symbol
temperature_sync_time_sec = 900 #how often to get weather data from HA in seconds. For example, once in 15*60seconds

# Service config (parameters description might be tricky and not very straightforward. Change only if you know what you are doing!)
cycle_time_ms = 200 # the main cycle delay. if sest to higher values than 200 ms seconds display doesn't feel smooth enough. It didn't affect the current draw.
cycle_time_ms_no_sec = 60000 # the main cycle delay if no seconds are displayed
max_wait_wifi_attempt_sec = 10 # time in seconds to wait for the wifi to become connected after the request to connect was sent
wifi_reconnect_time = 5 # time in seconds to wait before next attempt to connect to WiFi is permormed
wifi_reconnect_attempts_per_attempt = 2 # how many times per WiFi attempt to connect cycle to try to connect.
wifi_wait_time_per_attempt = 15 # how long to wait (in seconds) per attempt to connect to wifi per attempt
wifi_wait_time_step = 1 # how long (in seconds) to wait between attempts in wifi connect attempt cycle
