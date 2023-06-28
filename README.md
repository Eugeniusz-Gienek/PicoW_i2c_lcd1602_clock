# PicoW_i2c_lcd1602_clock
The simple digital clock, built using Pico W, LCD 1602 with i2c interface

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
* Screen: HD44780
* I2C Controller: PCF8574T
* Raspberry Pi Pico W
* 4 cables with connectors male-female
* MicroUSB cable
* (optional) Screen holder

Scheme:
![Connection scheme](./.readme/LCD1602_I2C_PICO_W_Scheme.png "Scheme")

Working result:
![Result](./.readme/repository-open-graph-1602-i2c-pico-w.png "Result")

Screen holder:
![Scheen holder 1](./.readme/OBUDOWA-AKRYLOWA-UCHWYT-DO-WYSWIETLACZA-LCD-1602.jpg "ScreenHolder1")

![Scheen holder 2](./.readme/OBUDOWA-AKRYLOWA-UCHWYT-DO-WYSWIETLACZA-LCD-1602-Kod-producenta-OBUDOWA-AKRYLOWA-UCHWYT-DO-WYSWIETLACZA.jpg "ScreenHolder2")

![Scheen holder 3](./.readme/OBUDOWA-AKRYLOWA-UCHWYT-DO-WYSWIETLACZA-LCD-1602-EAN-GTIN-5903689136150.webp "ScreenHolder3")
