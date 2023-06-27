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
import secrets
import time

import struct
import socket

from secrets import WIFI_SSID, WIFI_PASSWORD

NTP_DELTA = 2208988800
ntp_host = ["0.europe.pool.ntp.org", "1.europe.pool.ntp.org", "2.europe.pool.ntp.org", "3.europe.pool.ntp.org"]
tm_year = 0
tm_mon = 1 # range [1, 12]
tm_mday = 2 # range [1, 31]
tm_hour = 3 # range [0, 23]
tm_min = 4 # range [0, 59]
tm_sec = 5 # range [0, 61] in strftime() description
tm_wday = 6 # range 8[0, 6] Monday = 0
tm_yday = 7 # range [0, 366]
tm_isdst = 8 # 0, 1 or -1 


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

def q_set_time():
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1B
    time_is_set = False
    for host in ntp_host:
        addr = socket.getaddrinfo(host, 123)[0][-1]
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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
        return True
    else:
        print("Could not sync time...")
        return False

def req_attention():
    for i in range(5):
        lcd.backlight_off()
        time.sleep(0.2)
        lcd.backlight_on()
        time.sleep(0.4)

lcd.blink_cursor_on()
lcd.backlight_on()
lcd.clear()

max_wait = 10
wifi_reconnect_time = 5
wifi_wait_time = 5

while True:
    wifi_connected = False
    lcd.blink_cursor_on()
    lcd.show_cursor()
    lcd.putstr("Connecting to Wifi...")
    # Connect to wifi firstly
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    time.sleep(wifi_wait_time)
    lcd.clear()
    lcd.putstr("Wifi connection:\n")
    wifi_connected = wlan.isconnected()
    lcd.putstr(("Success\n" if wifi_connected else "Fail\n"))
    if wifi_connected:
        lcd.clear()
        lcd.putstr("NTP sync...\n")
        # Let's sync with NTP server
        while max_wait > 0:
            if wlan.status() < 0 or wlan.status() >= 3:
                break
            max_wait -= 1
            #print('Waiting for connection...')
            time.sleep(1)
        if wlan.status() != 3:
            lcd.clear()
            lcd.putstr("WiFi error.\n")
            lcd.putstr("Reconnect in "+str(wifi_reconnect_time)+"s")
            req_attention()
            wlan.active(False)
            time.sleep(wifi_reconnect_time)
            continue
        else:
            #sync time
            lcd.clear()
            lcd.putstr("Syncing time...\n")
            try:
                time_set_status = q_set_time()
                if time_set_status:
                    lcd.clear()
                    lcd.putstr("Synced.\n")
                    print("Sync really successfull.")
                else:
                    raise Exception("Sync error.")
            except Exception as e:
                print("Sync exception!")
                print("Error message: "+str(e))
                lcd.clear()
                lcd.putstr("Sync error.\n")
                req_attention()
                wlan.active(False)
                time.sleep(wifi_reconnect_time)
                continue
        lcd.blink_cursor_off()
        lcd.hide_cursor()
        last_date = ""
        while True:
            #show date and time
            t = cet_time()
            #t[tm_year], t[tm_mon], t[tm_mday], t[tm_wday] + 1, t[tm_hour], t[tm_min], t[tm_sec]
            #lcd.clear()
            new_date = ""+str((("0"+str(t[tm_mday])) if (t[tm_mday]<10) else str(t[tm_mday])))+"/"+str((("0"+str(t[tm_mon])) if (t[tm_mon]<10) else str(t[tm_mon])))+"/"+str(t[tm_year])+"\n"
            if new_date != last_date:
                lcd.move_to(0,0)
                lcd.putstr(new_date)
                last_date = new_date
            lcd.move_to(0,1)
            lcd.putstr(""+str((("0"+str(t[tm_hour])) if (t[tm_hour]<10) else str(t[tm_hour])))+":"+str((("0"+str(t[tm_min])) if (t[tm_min]<10) else str(t[tm_min])))+":"+str((("0"+str(t[tm_sec])) if (t[tm_sec]<10) else str(t[tm_sec]))))
            time.sleep(1)
    #wait till next WiFi connect iteration
    wlan.active(False)
    time.sleep(wifi_reconnect_time)
