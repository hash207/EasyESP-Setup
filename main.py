import esptool
from time import sleep
from pywifi import PyWiFi, const
from customtkinter import *
from subprocess import run
import serial.tools.list_ports
from tkinter import filedialog, messagebox

def esp32_code(ssid, pwd, pub_topic, sub_topic):
    return f"""#include <WiFi.h>
#include <PubSubClient.h>

// Update these with values suitable for your network.

const char* ssid = "{ssid}";
const char* password = "{pwd}";
const char* mqtt_server = "broker.emqx.io";
const int mqtt_port = 1883;
const int MQTT_LED = 0;
const int WiFi_LED = 1;

// Choose your pins (Example: RX=20, TX=21)

#define RX_PIN 20
#define TX_PIN 21

WiFiClient espClient;
PubSubClient client(espClient);
unsigned long lastMsg = 0;
#define MSG_BUFFER_SIZE	(50)
char msg[MSG_BUFFER_SIZE];
int value = 0;
float lastValue = 0.0;
String data;

void setup_wifi() {{

  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {{
    delay(500);
    Serial.print(".");
    digitalWrite(WiFi_LED,  !digitalRead(WiFi_LED));
  }}

  randomSeed(micros());

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  digitalWrite(WiFi_LED,  1);
}}

void callback(char* topic, byte* payload, unsigned int length) {{
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");

  String message = "";
  for (int i = 0; i < length; i++) {{
    message += (char)payload[i];
  }}

  Serial.println(message);
  Serial1.println(message);
}}

void reconnect() {{
  // Loop until we're reconnected
  while (!client.connected()) {{
    Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    digitalWrite(MQTT_LED, !digitalRead(0));
    if (client.connect(clientId.c_str())) {{
      Serial.println("connected");
      client.subscribe("{sub_topic}");
      digitalWrite(MQTT_LED, 1);
    }} else {{
      digitalWrite(MQTT_LED, 0);
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 2 seconds");
      // Wait 2 seconds before retrying
      delay(2000);
    }}
  }}
}}

void sendData()  {{
  if (Serial.available()){{
    data = Serial.readStringUntil('/');
    Serial.println(data);
    client.publish("{pub_topic}", data.c_str());
  }}
}}

void setup() {{
  pinMode(BUILTIN_LED, OUTPUT);     // Initialize the BUILTIN_LED pin as an output
  pinMode(0, OUTPUT);
  pinMode(1, OUTPUT);
  Serial.begin(9600);
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  // This initializes the hardware UART1 with your chosen pins
  Serial1.begin(9600, SERIAL_8N1, RX_PIN, TX_PIN);
}}

void loop() {{

  if (!client.connected()) {{
    reconnect();
  }}
  client.loop();

  sendData();

}}
"""

def esp8266_code(ssid, pwd, pub_topic, sub_topic): 
    return f"""#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <SoftwareSerial.h>

const char* ssid = "{ssid}";
const char* password = "{pwd}";
const char* mqtt_server = "broker.emqx.io";
const int mqtt_port = 1883;
const int MQTT_LED = D0;
const int WiFi_LED = D1;

WiFiClient espClient;
PubSubClient client(espClient);

// RX = D1 (GPIO 5) 
// TX = D2 (GPIO 4)
SoftwareSerial arduino(D2, D3); // RX, TX

void setup_wifi() {{

  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {{
    delay(500);
    Serial.print(".");
    digitalWrite(WiFi_LED,  !digitalRead(WiFi_LED));
  }}

  randomSeed(micros());

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  digitalWrite(WiFi_LED,  1);
}}

void callback(char* topic, byte* payload, unsigned int length) {{
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");

  String message = "";
  for (int i = 0; i < length; i++) {{
    message += (char)payload[i];
  }}

  Serial.println(message);
  arduino.println(message);
}}

void reconnect() {{
  // Loop until we're reconnected
  while (!client.connected()) {{
    Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    digitalWrite(MQTT_LED, !digitalRead(0));
    if (client.connect(clientId.c_str())) {{
      Serial.println("connected");
      client.subscribe("{sub_topic}");
      digitalWrite(MQTT_LED, 1);
    }} else {{
      digitalWrite(MQTT_LED, 0);
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 2 seconds");
      // Wait 2 seconds before retrying
      delay(2000);
    }}
  }}
}}

String reciev(){{
  String incomingMessage;
  if (arduino.available() > 0) {{
    
    // Read the incoming data until the newline character '/n'
    // This captures the whole string sent by nodemcu.println()
    incomingMessage += arduino.readStringUntil('/n');
    Serial.println(incomingMessage);
    client.publish("{pub_topic}", incomingMessage.c_str());
    
  }}
  return incomingMessage;
}}

void setup() {{
  // Initialize Serial Monitor (to view results on PC)
  Serial.begin(9600);
  
  // Initialize communication with Arduino
  arduino.begin(9600);
  
  Serial.println("NodeMCU ready to receive strings...");
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
}}

void loop() {{
  if (!client.connected()) {{
    reconnect();
  }}
  client.loop();

  reciev();
}}"""

def flash_esp_direct(port, path, title, is_esp8266=False):
    if not is_esp8266:
        # compile the sketch first (you can replace this with your actual sketch path)
        run(["arduino-cli", "compile", "-b", "esp32:esp32:esp32c3", "-e", path])
        
        # First, erase the flash to ensure a clean slate
        command_args = [
            "--chip", "esp32c3",
            "--port", port,
            "erase-flash"
        ]
        print(f"Erasing flash on {port}...")
        esptool.main(command_args)
        
        # Construct the arguments just like the command line, but omit "esptool.py"
        command_args = [
            "--chip", "esp32c3",
            "--port", port,
            "--baud", "460800",
            "write-flash",
            "0x0",
            path + r"\build\esp32.esp32.esp32c3\\" + title + r".ino.merged.bin"
        ]
    else:
        # For ESP8266, the process is similar but with different parameters
        run(["arduino-cli", "compile", "-b", "esp8266:esp8266:nodemcuv2", "-e", path])
        
        command_args = [
            "--chip", "esp8266",
            "--port", port,
            "--baud", "115200",
            "write-flash",
            "--flash-mode", "dio",
            "0x00000",
            path + r"\build\esp8266.esp8266.nodemcuv2\\" + title + r".ino.bin"
        ]
    
    print(f"Initializing esptool on {port}...")
    
    try:
        # Pass the arguments directly to esptool's main entry point
        esptool.main(command_args)
        print("\n✅ Flashing completed successfully!")
        
    except Exception as e:
        # esptool will raise exceptions if the board isn't found or communication fails
        print(f"\n❌ Flashing failed: {e}")

def get_ssids():
    iface = PyWiFi().interfaces()[0] # Selects the first wireless adapter

    iface.scan() # Trigger a scan
    sleep(5) # Give it a moment to find networks
    
    results = iface.scan_results()
    
    ssids = list(set([network.ssid for network in results]))
    
    return ssids

class main_frame(CTkFrame):
    def __init__(self ,master):
        super().__init__(master, height=400, width=800)
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)
        
        label1 = CTkLabel(self, text="Project's Name: ", font=("Arial", 30))
        label1.grid(row=0, column=0, sticky="ew")
        self.title = CTkEntry(self, placeholder_text="Enter project name")
        self.title.grid(row=0, column=1, columnspan=3, padx=5, sticky="ew")
        label2 = CTkLabel(self, text="WiFi configurations: ", font=("Arial", 24))
        label2.grid(row=1, column=0, sticky="ew")
        self.ssid = CTkEntry(self, placeholder_text="SSID")
        self.ssid.grid(row=1, column=1, padx=5, sticky="ew")
        wifi = CTkButton(self, text="WiFi List", width= 50, command=self.wifi_info)
        wifi.grid(row=1, column=2, padx=5, sticky="ew")
        self.pwd = CTkEntry(self, placeholder_text="Password", show="*")
        self.pwd.grid(row=1, column=3, padx=5, sticky="ew")
        label3 = CTkLabel(self, text="MQTT topic to publish: ", font=("Arial", 24))
        label3.grid(row=2, column=0, sticky="ew")
        self.pub_topic = CTkEntry(self, placeholder_text="MQTT Publish Topic")
        self.pub_topic.grid(row=2, column=1, padx=5, columnspan=3, sticky="ew")
        label4 = CTkLabel(self, text="MQTT topic to subscribe: ", font=("Arial", 24))
        label4.grid(row=3, column=0, sticky="ew")
        self.sub_topic = CTkEntry(self, placeholder_text="MQTT Subscribe Topic")
        self.sub_topic.grid(row=3, column=1, padx=5, columnspan=3, sticky="ew")
        btn = CTkButton(self, text="Submit", command=self.submit_action)
        btn.grid(row=4, column=1, sticky="ew")
        upload = CTkButton(self, text="Flash to ESP", command= self.flash_action)
        upload.grid(row=5, column=1, sticky="ew")
        self.chk = CTkCheckBox(self, text="ESP8266", onvalue=True, offvalue=False)
        self.chk.grid(row=4, column=2, sticky="ew")

    def is_empty(self):
        required_entries = {
                    "Project's Name": self.title,
                    "WiFi SSID": self.ssid,
                    "WiFi Password": self.pwd,
                    "MQTT Publish Topic": self.pub_topic,
                    "MQTT Subscribe Topis": self.sub_topic
                }
        empty_fields = [name for name, entry in required_entries.items() if not entry.get()]
        return empty_fields

    def submit_action(self):
        print(self.is_empty())
        if not self.is_empty():
            dir = filedialog.askdirectory(title="Please select a directory")
            save_dir = dir if dir else None
            if save_dir:
                print(f"File save at: {save_dir}")
                
                try:
                    os.mkdir(f"{save_dir}/{self.title.get()}")
                except FileExistsError:
                    result = messagebox.askyesno("Error", f"A folder named '{self.title.get()}' already exists in the selected directory. Do you want to overwrite it?")
                    if not result:
                        return
                    
                with open(f"{save_dir}/{self.title.get()}/{self.title.get()}.ino", "wt") as f:
                    _code = esp8266_code(self.ssid.get(), self.pwd.get(), self.pub_topic.get(), self.sub_topic.get()) if self.chk.get() else esp32_code(self.ssid.get(), self.pwd.get(), self.pub_topic.get(), self.sub_topic.get())
                    f.write(_code.replace("/n", "\\n"))
                return save_dir
            else:
                messagebox.showerror("Error", "No directory selected. Please try again.")
        else:
            messagebox.showerror("Error: Empty Fields", f"The following fields are empty: {', '.join(self.is_empty())}")

    def flash_action(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        if len(ports) == 0:
            messagebox.showerror("Error", "No serial ports found. Please connect your ESP device and try again.")
        elif len(ports) > 1:
            messagebox.showerror("Error", f"Multiple serial ports found: {', '.join(ports)}. Please ensure only one ESP device is connected and try again.")
        else:
            port = ports[0]
            skitch_path = str(self.submit_action()) + "/" + self.title.get()  # Ensure the sketch is generated before flashing
            if skitch_path:
                flash_esp_direct(port, skitch_path, self.title.get(), is_esp8266=self.chk.get())
            else:
                messagebox.showerror("Error", "Sketch generation failed. Please fix the errors and try again.")

    def wifi_info(self):
        wifi = PyWiFi()
        
        # 1. Crash Prevention: Check if the computer even has a Wi-Fi adapter
        if not wifi.interfaces():
            messagebox.showerror("Hardware Error", "No Wi-Fi adapter found on this device!")
            return
            
        iface = wifi.interfaces()[0]

        # 2. Check the connection status
        # const.IFACE_CONNECTED means the adapter is currently linked to a router
        if iface.status() != const.IFACE_CONNECTED:
            
            # Ask the user if they still want to scan using a Yes/No pop-up
            msg = "You are not currently connected to a Wi-Fi network.\n\nDo you still want to scan for available networks?"
            should_scan = messagebox.askyesno("Not Connected", msg)
            
            # If they click 'No', exit the function early
            if not should_scan:
                return 

        # 3. If connected (or if they clicked 'Yes'), proceed with creating the window
        win = CTkToplevel(self)
        win.title("WiFi List")
        win.attributes("-topmost", True)
        
        # Show the loading label immediately
        loading_label = CTkLabel(win, text="Scanning for networks...\nPlease wait 5 seconds.", font=("Arial", 16))
        loading_label.pack(padx=40, pady=40)
        
        def on_closing(selected_ssid):
            self.ssid.delete(0, END)
            self.ssid.insert(0, selected_ssid)
            win.destroy()
            
        def fetch_and_display(interface):
            results = interface.scan_results()
            ssids = list(set([network.ssid for network in results if network.ssid]))
            
            loading_label.destroy()
            
            for ssid_name in ssids:
                btn = CTkButton(win, text=ssid_name, command=lambda s=ssid_name: on_closing(s))
                btn.pack(padx=10, pady=5)
                
        # Trigger the scan and set the 5-second timer
        iface.scan()
        win.after(5000, lambda: fetch_and_display(iface))

class main_app(CTk):
    def __init__(self):
        super().__init__()
        self.title("ESP32/ESP8266 - Arduino MQTT Setup")
        self.geometry("800x400")
        self.protocol("WM_DELETE_WINDOW", self.EXIT)
        
        frame = main_frame(self)
        frame.pack()        
        
        self.mainloop()

    def EXIT(self):
        res = messagebox.askyesno('EasyESP-Setup', 'Are you sure you want to leave?')
        if res == 1:
            self.destroy()
        return

if __name__ == "__main__":
    main_app()