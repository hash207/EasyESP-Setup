from time import sleep
from pywifi import PyWiFi
from customtkinter import *
from tkinter import filedialog

esp32_code = lambda ssid, pwd, topic: f"""#include <WiFi.h>
#include <PubSubClient.h>

// Update these with values suitable for your network.

const char* ssid = "{ssid}";
const char* password = "{pwd}";
const char* mqtt_server = "broker.emqx.io";
const int mqtt_port = 1883;
const int MQTT_LED = 0;
const int WiFi_LED = 1;

WiFiClient espClient;
PubSubClient client(espClient);
unsigned long lastMsg = 0;
#define MSG_BUFFER_SIZE	(50)
char msg[MSG_BUFFER_SIZE];
int value = 0;
float lastValue = 0.0;
String data;

void setup_wifi() *(

  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) *(
    delay(500);
    Serial.print(".");
    digitalWrite(WiFi_LED,  !digitalRead(1));
  )*

  randomSeed(micros());

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  digitalWrite(WiFi_LED,  1);
)*

void callback(char* topic, byte* payload, unsigned int length) *(
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) *(
    Serial.print((char)payload[i]);
  )*
  Serial.println();
)*

void reconnect() *(
  // Loop until we're reconnected
  while (!client.connected()) *(
    Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    digitalWrite(MQTT_LED, !digitalRead(0));
    if (client.connect(clientId.c_str())) *(
      Serial.println("connected");
      client.subscribe("HashESP1");
      digitalWrite(MQTT_LED, 1);
    )* else *(
      digitalWrite(MQTT_LED, 0);
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 2 seconds");
      // Wait 2 seconds before retrying
      delay(2000);
    )*
  )*
)*

void sendData()  *(
  if (Serial.available())*(
    data = Serial.readStringUntil('/');
    Serial.println(data);
    client.publish("{topic}", data.c_str());
  )*
)*

void setup() *(
  pinMode(BUILTIN_LED, OUTPUT);     // Initialize the BUILTIN_LED pin as an output
  pinMode(0, OUTPUT);
  pinMode(1, OUTPUT);
  Serial.begin(9600);
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
)*

void loop() *(

  if (!client.connected()) *(
    reconnect();
  )*
  client.loop();

  sendData();

)*
"""

esp8266_code = lambda ssid, pwd, topic: f"""#include <ESP8266WiFi.h>
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
SoftwareSerial arduino(D1, D2); 

void setup_wifi() *(

  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) *(
    delay(500);
    Serial.print(".");
    digitalWrite(WiFi_LED,  !digitalRead(1));
  )*

  randomSeed(micros());

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  digitalWrite(WiFi_LED,  1);
)*

void callback(char* topic, byte* payload, unsigned int length) *(
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) *(
    Serial.print((char)payload[i]);
  )*
  Serial.println();
)*

void reconnect() *(
  // Loop until we're reconnected
  while (!client.connected()) *(
    Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    digitalWrite(MQTT_LED, !digitalRead(0));
    if (client.connect(clientId.c_str())) *(
      Serial.println("connected");
      client.subscribe("HashESP1");
      digitalWrite(MQTT_LED, 1);
    )* else *(
      digitalWrite(MQTT_LED, 0);
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 2 seconds");
      // Wait 2 seconds before retrying
      delay(2000);
    )*
  )*
)*

String reciev()*(
  String incomingMessage;
  if (arduino.available() > 0) *(
    
    // Read the incoming data until the newline character '/n'
    // This captures the whole string sent by nodemcu.println()
    incomingMessage += arduino.readStringUntil('/n');
    Serial.println(incomingMessage);
    client.publish("{topic}", incomingMessage.c_str());
    
  )*
  return incomingMessage;
)*

void setup() *(
  // Initialize Serial Monitor (to view results on PC)
  Serial.begin(9600);
  
  // Initialize communication with Arduino
  arduino.begin(9600);
  
  Serial.println("NodeMCU ready to receive strings...");
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
)*

void loop() *(
  if (!client.connected()) *(
    reconnect();
  )*
  client.loop();

  reciev();
)*"""

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
        self.grid_rowconfigure((0, 1, 2, 3), weight=1)
        
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
        self.topic = CTkEntry(self, placeholder_text="MQTT Topic")
        self.topic.grid(row=2, column=1, padx=5, columnspan=3, sticky="ew")
        btn = CTkButton(self, text="Submit", command=self.submit_action)
        btn.grid(row=3, column=1, sticky="ew")
        self.chk = CTkCheckBox(self, text="ESP8266", onvalue=True, offvalue=False)
        self.chk.grid(row=3, column=2, sticky="ew")

    def submit_action(self):
        print(self.chk.get())
        save_dir = filedialog.askdirectory(title="Please select a directory")
        print(f"File save at: {save_dir}")
        
        os.mkdir(f"{save_dir}/{self.title.get()}")
        
        with open(f"{save_dir}/{self.title.get()}/{self.title.get()}.ino", "wt") as f:
            _code = esp8266_code(self.ssid.get(), self.pwd.get(), self.topic.get()) if self.chk.get() else esp32_code(self.ssid.get(), self.pwd.get(), self.topic.get())
            f.write(_code.replace("*(", "{").replace(")*", "}").replace("/n", "\\n"))

    def wifi_info(self):
            win = CTkToplevel(self)
            win.title("WiFi List")
            win.attributes("-topmost", True)
            
            # 1. Show the loading label immediately
            loading_label = CTkLabel(win, text="Scanning for networks...\nPlease wait 5 seconds.", font=("Arial", 16))
            loading_label.pack(padx=40, pady=40)
            
            def on_closing(selected_ssid):
                # Print to console for debugging
                print(f"Selected SSID: {selected_ssid}")
                
                self.ssid.delete(0, END)
                self.ssid.insert(0, selected_ssid)
                
                win.destroy()
                
            def fetch_and_display(iface):
                # 4. This runs 5 seconds later to grab the results
                results = iface.scan_results()
                
                # Filter out empty SSIDs (PyWiFi sometimes catches hidden networks)
                ssids = list(set([network.ssid for network in results if network.ssid]))
                
                # Remove the loading label
                loading_label.destroy()
                
                # 5. Display the buttons
                for ssid_name in ssids:
                    # FIXED: Added s=ssid_name to avoid the lambda late-binding bug
                    btn = CTkButton(win, text=ssid_name, command=lambda s=ssid_name: on_closing(s))
                    btn.pack(padx=10, pady=5)
                    
            # 2. Initialize PyWiFi and trigger the scan
            wifi = PyWiFi()
            iface = wifi.interfaces()[0]
            iface.scan()
            
            # 3. Use .after() to wait 5 seconds (5000 milliseconds) WITHOUT blocking the GUI
            win.after(5000, lambda: fetch_and_display(iface))

class main_app(CTk):
    def __init__(self):
        super().__init__()
        self.title("ESP32/ESP8266 - Arduino MQTT Setup")
        self.geometry("800x400")
        
        frame = main_frame(self)
        frame.pack()        
        
        self.mainloop()

if __name__ == "__main__":
    main_app()