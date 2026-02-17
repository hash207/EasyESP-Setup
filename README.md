# ESP-MQTT Configurator ⚡

A desktop automation tool built with Python and CustomTkinter that generates ready-to-use WiFi and MQTT boilerplate code for ESP32 and ESP8266 microcontrollers.

## 📖 About The Project

When building IoT projects, setting up the basic WiFi connection and MQTT client loops can be incredibly repetitive. This application solves that by providing a clean, dark-mode GUI to input your project details and instantly export a fully functioning `.ino` template. 

Instead of manually typing out your network credentials, the app includes a built-in WiFi scanner that detects available networks around you, saving time and preventing typos. 

### ✨ Key Features
* **Automated Code Generation:** Instantly outputs `.ino` files configured for your specific microcontroller.
* **Hardware Toggling:** Seamlessly switch between ESP32 and ESP8266 (NodeMCU) code templates.
* **Live WiFi Scanning:** Uses `pywifi` to scan and list nearby SSIDs, allowing you to select your network with one click.
* **Built-in Error Handling:** Validates all user inputs before generating files to prevent broken directories or missing variables.
* **Modern UI:** Built with `customtkinter` for a sleek, responsive, and modern interface.

## 🚀 Getting Started

### Prerequisites
Make sure you have Python installed, then install the required libraries:
```bash
pip install customtkinter pywifi 
```
(Note: You may also need comtypes on Windows for pywifi to work properly).

Installation & Usage
1. Clone the repository:

```
git clone [https://github.com/yourusername/ESP-MQTT-Configurator.git](https://github.com/yourusername/ESP-MQTT-Configurator.git)
```

2. Navigate to the project directory:
```
cd ESP-MQTT-Configurator
```

3. Run the application:
```
python main.py
```

4. Enter your project name, select your WiFi network, input the password, and set your MQTT topic.

5. Choose your board (ESP32 checkbox) and hit Submit.

6. Select the folder where you want your project saved. The app will generate a ready-to-flash Arduino IDE folder and file!

## 🛠️ Built With

* [Python 3](https://www.python.org/)

* [CustomTkinter](https://customtkinter.tomschimansky.com/documentation/) - For the modern UI

* [PyWiFi](https://github.com/awkman/pywifi/tree/master) - For network scanning



