# PicoW_i2c_lcd1602_clock
The simple digital clock, which syncs with NTP server via WiFi.
Built using Pico W, LCD 1602 with i2c interface

In order to make it work:

1. Software:
  * Download repo
  * Copy secrets_dist.py file to secrets.py file
  * Adjust data in secrets.py file
2. Hardware:
  * Connect LCD 1602 VCC to Pico VBUS pin
  * Connect LCD 1602 GND to any Pico GND pin (for example, 38th)
  * Connect LCD 1602 SDA to Pico GP0 pin
  * Connect LCD 1602 SCL to Pico GP1 pin
3. Connect altogether:
  * Thonny - install micropython;
  * Upload the files to Pico;
  * Reset and disconnect from PC;
  * Done!

Components list:
* **Screen: HD44780**<br/> <sub><sup>_(screen and I2C can be bought for example [here](https://botland.store/alphanumeric-and-graphic-displays/2351-lcd-display-2x16-characters-blue-i2c-lcm1602-5904422309244.html) )_</sup></sub>
* **I2C Controller: PCF8574T**
* **Raspberry Pi Pico W**<br/> <sub><sup>_(can be bought for example [here](https://botland.store/raspberry-pi-pico-modules-and-kits/21574-raspberry-pi-pico-w-rp2040-arm-cortex-m0-cyw43439-wifi-5056561803173.html) )_</sup></sub>
* **4 cables with connectors male-female**<br/> <sub><sup>_(can be bought for example [here](https://botland.store/female-to-male-connecting-cables/19949-connecting-cables-female-male-justpi-10cm-40pcs-5904422328696.html) )_</sup></sub>
* **MicroUSB cable**<br/> <sub><sup>_(can be bought for example [here](https://botland.store/usb-20-cables/2906-microusb-cable-b-a-1m-5901812014474.html) )_</sup></sub>
* _(optional)_ **Screen holder**<br/> <sub><sup>_(can be bought for example [here](https://botland.store/alphanumeric-and-graphic-displays/10914-stand-for-lcd-display-2x16-characters-5904422317027.html) )_</sup></sub>

Scheme:
![Connection scheme](./.readme/LCD1602_I2C_PICO_W_Scheme.png "Scheme")

Working result:
![Result](./.readme/repository-open-graph-1602-i2c-pico-w.png "Result")

Screen holder:

![Scheen holder 1](./.readme/OBUDOWA-AKRYLOWA-UCHWYT-DO-WYSWIETLACZA-LCD-1602.jpg "ScreenHolder1")

![Scheen holder 2](./.readme/OBUDOWA-AKRYLOWA-UCHWYT-DO-WYSWIETLACZA-LCD-1602-Kod-producenta-OBUDOWA-AKRYLOWA-UCHWYT-DO-WYSWIETLACZA.jpg "ScreenHolder2")

![Scheen holder 3](./.readme/OBUDOWA-AKRYLOWA-UCHWYT-DO-WYSWIETLACZA-LCD-1602-EAN-GTIN-5903689136150.webp "ScreenHolder3")
