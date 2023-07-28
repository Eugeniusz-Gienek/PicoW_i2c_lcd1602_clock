# /**
#   ******************************************************************************
#   * @file    main.py
#   * @author  Eugene at sky.community
#   * @version V1.0.0
#   * @date    28-June-2023
#   * @brief   The PicoW I2C LCD 1602 display clock.
#   *
#   ******************************************************************************
#   */
from machine import I2C, Pin

from pico_i2c_lcd import I2cLcd
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)

I2C_ADDR = i2c.scan()[0]
lcd = I2cLcd(i2c, I2C_ADDR, 2, 16)

import network
from network import WLAN
import secrets
import time

import struct
import usocket

import urequests

import uasyncio

from secrets import WIFI_SSID, WIFI_PASSWORD
from secrets import HA_TOKEN
from config import ntp_host
from config import max_wait_wifi_attempt_sec, wifi_reconnect_time, wifi_wait_time_per_attempt, wifi_wait_time_step, wifi_reconnect_attempts_per_attempt
from config import ha_api_url_temperature, ha_api_temperature_json_path, temperature_sync_time_sec, temperature_units
from config import wifi_ip_config
from config import ntp_srv_timeout
from config import ha_srv_timeout


NTP_DELTA = 2208988800
tm_year = 0
tm_mon = 1 # range [1, 12]
tm_mday = 2 # range [1, 31]
tm_hour = 3 # range [0, 23]
tm_min = 4 # range [0, 59]
tm_sec = 5 # range [0, 61] in strftime() description
tm_wday = 6 # range 8[0, 6] Monday = 0
tm_yday = 7 # range [0, 366]
tm_isdst = 8 # 0, 1 or -1 

ha_headers = {
    "Authorization": "Bearer "+HA_TOKEN,
}

time_was_synced = False
time_was_synced_at_least_once = False
last_temp_set = False
last_temp_value = None
wlan_power_config = None
wlan_already_tried_perf_mode = False
#wlan_power_config = network.WLAN.PM_POWERSAVE

def cet_time():
    year = time.localtime()[0]       #get current year
    HHMarch   = time.mktime((year,3 ,(31-(int(5*year/4+4))%7),1,0,0,0,0,0)) #Time of March change to CEST
    HHOctober = time.mktime((year,10,(31-(int(5*year/4+1))%7),1,0,0,0,0,0)) #Time of October change to CET
    now=time.time()
    offet_base = 0
    if now < HHMarch :               # we are before last sunday of march
        cet=time.localtime(now+offet_base) # CET:  UTC+1H
    elif now < HHOctober :           # we are before last sunday of october
        cet=time.localtime(now+offet_base+3600) # CEST: UTC+2H
        #print("we are before last sunday of october")
    else:                            # we are after last sunday of october
        cet=time.localtime(now+offet_base) # CET:  UTC+1H
        #print("we are after last sunday of october")
    return(cet)

async def q_set_time():
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1B
    time_is_set = False
    print("Attempt to set time.\n")
    for host in ntp_host:
        print("Trying with NTP host: "+host)
        addr = usocket.getaddrinfo(host, 123)[0][-1]
        try:
            s = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM)
            try:
                s.settimeout(1)
                res = s.sendto(NTP_QUERY, addr)
                msg = s.recv(48)
            finally:
                s.close()
            val = struct.unpack("!I", msg[40:44])[0]
            t = val - NTP_DELTA    
            tm = time.gmtime(t)
            machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))
            time_is_set = True
        except OSError as exc:
            print("Could not get time from NTP host.")
            if exc.args[0] == 110: # ETIMEDOUT
                print("ETIMEDOUT for the host \""+str(host)+"\". Damn.\n")
                time_is_set = False
        if time_is_set:
            break
    if time_is_set:
        print("UTC time after synchronization：%s" %str(time.localtime()))
        t = cet_time()
        print("CET time after synchronization : %s" %str(t))
        machine.RTC().datetime((t[tm_year], t[tm_mon], t[tm_mday], t[tm_wday] + 1, t[tm_hour], t[tm_min], t[tm_sec], 0))
        print("Local time after synchronization：%s" %str(time.localtime()))
        print("NTP sync successful.");
        global time_was_synced
        time_was_synced = True
        return True
    else:
        print("Could not sync time...")
        time_was_synced = False
        return False


async def q_try_set_time():
    t = uasyncio.create_task(q_set_time())
    await uasyncio.sleep(0)
    #print("Waiting "+str(ntp_srv_timeout+1)+" seconds for NTP.")
    uasyncio.wait_for(t,ntp_srv_timeout)
    #await uasyncio.sleep(ntp_srv_timeout+1)
    print("Done.")
    global time_was_synced
    return time_was_synced

def req_attention():
    for i in range(5):
        lcd.backlight_off()
        time.sleep(0.2)
        lcd.backlight_on()
        time.sleep(0.4)

async def get_current_temperature_async(t_url, hrds, t_json_path):
    global last_temp_set
    global last_temp_value
    try:
        response = urequests.request("GET", t_url, headers=hrds)
    except:
        response = None
    try:
        local_temp = eval("response.json()"+t_json_path,{"__builtins__" : None },{'response': response})
        last_temp_set = True
        last_temp_value = local_temp
    except (SyntaxError, ValueError, AttributeError, NameError, TypeError, ZeroDivisionError):
        local_temp = None
        last_temp_set = False
        print("Incorrect data in temperature json path. Please fix the config")
    return local_temp

async def get_current_temperature(t_url, hrds, t_json_path):
    global last_temp_set
    global last_temp_value
    last_temp_set = False
    last_temp_value = None
    t = uasyncio.create_task(get_current_temperature_async(t_url, hrds, t_json_path))
    await uasyncio.sleep(0)
    #print("Waiting "+str(ha_srv_timeout+1)+" seconds for HA.")
    uasyncio.wait_for(t,ha_srv_timeout)
    #time.sleep(ha_srv_timeout+1)
    print("Done.")
    return last_temp_value

lcd.blink_cursor_on()
lcd.backlight_on()
lcd.clear()
degrees = bytes([0x7, 0x5, 0x7, 0x0, 0x0, 0x0, 0x0, 0x0])
lcd.custom_char(0, degrees)
wifi = (0b00000,0b01110,0b10001,0b00100,0b01010,0b00000,0b00100,0b00000)
lcd.custom_char(1, wifi)
nowifi =  (0b00001,0b01110,0b10011,0b00100,0b01110,0b01000,0b10100,0b00000)
lcd.custom_char(2, nowifi)
max_wait_wifi_sec = max_wait_wifi_attempt_sec * wifi_reconnect_attempts_per_attempt



while True:
    wifi_connected = False
    lcd.blink_cursor_on()
    lcd.show_cursor()
    lcd.move_to(0,0)
    lcd.clear()
    lcd.move_to(0,0)
    lcd.putstr("Connecting to Wifi...")
    # Connect to wifi firstly
    wlan = network.WLAN(network.STA_IF)
    #wlan.config(wlan_power_config)
    wlan.active(True)
    if(wifi_ip_config['mode'] == 'static'):
        wlan.ifconfig((wifi_ip_config['params']['ip'],wifi_ip_config['params']['mask'],wifi_ip_config['params']['gateway'],wifi_ip_config['params']['dns']))
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    temp_sec_cntr_chk = time.time()
    temp_sec_cntr_chk_init = temp_sec_cntr_chk
    wifi_indicator_status_i = False
    init_str_l = max(len(str(wifi_wait_time_per_attempt * wifi_reconnect_attempts_per_attempt)),1)
    curr_str_l = init_str_l
    attempt = 0
    while(attempt < wifi_reconnect_attempts_per_attempt):
        while(((temp_sec_cntr_chk - temp_sec_cntr_chk_init) < wifi_wait_time_per_attempt) and (not wifi_indicator_status_i)):
            time_left = (wifi_wait_time_per_attempt*(wifi_reconnect_attempts_per_attempt-attempt))-(temp_sec_cntr_chk - temp_sec_cntr_chk_init)
            curr_str_l = max(len(str(time_left)),1)
            if(curr_str_l < init_str_l):
                lcd.move_to(16-init_str_l,1)
                lcd.putstr(" "*init_str_l)
                init_str_l -= 1
            lcd.move_to(16-curr_str_l,1)
            lcd.putstr(str(time_left))
            time.sleep(wifi_wait_time_step)
            temp_sec_cntr_chk = time.time()
            wifi_indicator_status_i = wlan.isconnected()
        wifi_connected_status = wlan.status()
        if(wifi_indicator_status_i):
            break
        if(wifi_connected_status != network.STAT_CONNECTING):
            break
        attempt+=1
        temp_sec_cntr_chk_init = temp_sec_cntr_chk
    lcd.clear()
    lcd.move_to(0,0)
    lcd.putstr("Wifi connection:\n")
    wifi_connected = wifi_indicator_status_i or wlan.isconnected()
    lcd.putstr(("Success\n" if wifi_connected else "Fail\n"))
    if wifi_connected:
        time_sync_progress = True
        lcd.clear()
        lcd.move_to(0,0)
        lcd.putstr("NTP sync...\n")
        # Let's sync with NTP server
        while max_wait_wifi_sec > 0:
            if wlan.status() < 0 or wlan.status() >= 3:
                break
            max_wait_wifi_sec -= 1
            #print('Waiting for connection...')
            time.sleep(1)
        if wlan.status() != 3:
            lcd.clear()
            lcd.putstr("WiFi error.\n")
            lcd.putstr("Reconnect in "+str(wifi_reconnect_time)+"s")
            req_attention()
            #wlan.active(False)
            #time.sleep(wifi_reconnect_time)
            #continue
            time_sync_progress = False
        else:
            #sync time
            lcd.clear()
            lcd.putstr("Syncing time...\n")
            try:
                uasyncio.run(q_try_set_time())
                time_set_status = time_was_synced
                if time_set_status:
                    lcd.clear()
                    lcd.putstr("Synced.\n")
                    time_was_synced_at_least_once = True
                else:
                    raise Exception("Time sync error!")
            except Exception as e:
                print("NTP sync exception!")
                print("Error message: "+str(e))
                print("Maybe NTP server unavailable?")
                lcd.clear()
                lcd.putstr("Time sync error!\n")
                req_attention()
                #wlan.active(False)
                #time.sleep(wifi_reconnect_time)
                #continue
                time_sync_progress = False
        if(time_sync_progress):
            lcd.blink_cursor_off()
            lcd.hide_cursor()
            last_date = ""
            # Get weather data
            lcd.clear()
            lcd.putstr("Syncing temperature...\n")
            temp_sec_cntr = time.time()
            old_current_temperature = None
            uasyncio.run(get_current_temperature(ha_api_url_temperature, ha_headers, ha_api_temperature_json_path))
            current_temperature = last_temp_value if last_temp_set else None
            print("Current temperature received: ", current_temperature)
            lcd.clear()
            lcd.putstr("Synced.\n")
            # EOF getting weather data
            lcd.move_to(15,0)
            lcd.putstr("\x01")
            wifi_down = False
            while True:
                #show date and time
                t = cet_time()
                temp_sec_cntr_chk = time.time()
                if(temp_sec_cntr_chk - temp_sec_cntr >= temperature_sync_time_sec):
                    uasyncio.run(get_current_temperature(ha_api_url_temperature, ha_headers, ha_api_temperature_json_path))
                    current_temperature = last_temp_value if last_temp_set else None
                    #print("Current temperature received: ", current_temperature)
                    temp_sec_cntr = time.time()
                #t[tm_year], t[tm_mon], t[tm_mday], t[tm_wday] + 1, t[tm_hour], t[tm_min], t[tm_sec]
                #lcd.clear()
                wday = ""
                if(t[tm_wday] == 0):
                    wday = "Mo"
                elif(t[tm_wday] == 1):
                    wday = "Tu"
                elif(t[tm_wday] == 2):
                    wday = "We"
                elif(t[tm_wday] == 3):
                    wday = "Th"
                elif(t[tm_wday] == 4):
                    wday = "Fr"
                elif(t[tm_wday] == 5):
                    wday = "Sa"
                elif(t[tm_wday] == 6):
                    wday = "Su"
                new_date = ""+str((("0"+str(t[tm_mday])) if (t[tm_mday]<10) else str(t[tm_mday])))+"/"+str((("0"+str(t[tm_mon])) if (t[tm_mon]<10) else str(t[tm_mon])))+"/"+str(t[tm_year])+"  "+wday+"\n"
                if new_date != last_date:
                    lcd.move_to(0,0)
                    lcd.putstr(new_date)
                    last_date = new_date
                lcd.move_to(0,1)
                lcd.putstr(""+str((("0"+str(t[tm_hour])) if (t[tm_hour]<10) else str(t[tm_hour])))+":"+str((("0"+str(t[tm_min])) if (t[tm_min]<10) else str(t[tm_min])))+":"+str((("0"+str(t[tm_sec])) if (t[tm_sec]<10) else str(t[tm_sec]))))
                if(old_current_temperature != current_temperature):
                    old_current_temperature = current_temperature
                    # output current temperature
                    lcd.move_to(10,1)
                    if (current_temperature != None):
                        lcd.putstr("" + f'{current_temperature:.1f}'+"\x00"+("C" if (temperature_units == "celsius") else "F" ))
                    else:
                        lcd.putstr(" ------")
                if current_temperature == None:
                    wifi_down = True
                    break
                time.sleep(0.5)
        else:
            pass
    lcd.move_to(0,0)
    lcd.clear()
    lcd.move_to(0,0)
    lcd.putstr("Wifi off.")
    lcd.move_to(0,1)
    lcd.putstr("Reconn. in:")
    lcd.move_to(16-len(str(wifi_reconnect_time)),1)
    lcd.putstr(str(wifi_reconnect_time))
    if (not wifi_connected):
        print("Could not connect to WiFi. WiFi status: ")
        wifi_status = wlan.status()
        if(wifi_status == network.STAT_IDLE):
            print("no connection and no activity")
        elif(wifi_status == network.STAT_CONNECTING):
            print("connecting was STILL in progress")
        elif(wifi_status == network.STAT_WRONG_PASSWORD):
            print("failed due to incorrect password")
        elif(wifi_status == network.STAT_NO_AP_FOUND):
            print("failed because no access point replied")
        elif(wifi_status == network.STAT_CONNECT_FAIL):
            print("failed due to other problems (some unknown ones)")
        elif(wifi_status == network.STAT_GOT_IP):
            print("connection successful - actually we've got an IP.")
        elif(wifi_status == 2):
            print("failed due to being unable to get IP address for some reason. Wifi connected though. DHCP problems?")
        else:
            print("connection unsuccessful - without any reason specified. Code: {}".format(wifi_status))
        #if(wlan_power_config != WLAN.PM_PERFORMANCE):
        #    print("Let's try to switch WiFi to performance mode. Maybe that will help?")
        #    wlan_power_config = WLAN.PM_PERFORMANCE
        #    wlan_already_tried_perf_mode = False
        #else:
        #    if(not wlan_already_tried_perf_mode):
        #        print("Well, the WiFi performance mode didn't help.")
        #        wlan_already_tried_perf_mode = True
    lcd.move_to(15,0)
    lcd.putstr("\x02")
    #wait till next WiFi connect iteration
    wlan.active(False)
    init_str_l = max(len(str(wifi_reconnect_time)),1)
    curr_str_l = init_str_l
    for i in range(wifi_reconnect_time):
        time_left = max(wifi_reconnect_time-i,0)
        curr_str_l = max(len(str(time_left)),1)
        if(curr_str_l < init_str_l):
            lcd.move_to(16-init_str_l,1)
            lcd.putstr(" "*init_str_l)
            init_str_l -= 1
        lcd.move_to(16-curr_str_l,1)
        lcd.putstr(str(time_left))
        time.sleep(1)
