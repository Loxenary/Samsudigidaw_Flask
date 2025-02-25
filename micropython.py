from machine import Pin
import dht
import time
import network
import ujson
import requests

led = Pin(2, Pin.OUT)
led.off()
sensor = dht.DHT11(Pin(5))
data = {}
ip = ""
token = "DavisSudahMandi"

print("Connecting to Wi-fi")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("Janati C10", "janatiparkc10")

while not wlan.isconnected():
    time.sleep(0.5)
    print("Connecting...")

print("Connected to Wi-Fi")
ip = wlan.ifconfig()[0]
print("IP Address:", ip)

# Check API Connection
try:
    print("HELLO CHECK API CONNECTION")
    url = "https://samsudigidaw.vtriadi.site/health"
    response = requests.get(url)
    if response.status_code == 200:
        print("Connection to API Successfull")
    else:
        print("FAILED TO CONNECT TO API")
except OSError as e:
    print(e)


while True:
    try:
        time.sleep(2)
        print("Re-Meassuring")
        sensor.measure()
        temp_data = {
            "temperature": sensor.temperature(),
            "humidity": sensor.humidity(),
            "batery": 30,
        }

        if temp_data != data:
            print("Updated!")
            led.on()
            data = temp_data.copy()
            print(data)
            requests.post(
                "https://samsudigidaw.vtriadi.site/data/" + token,
                json=data,
                headers={"Content-Type": "application/json"},
            )
            print("POST DATA")
            time.sleep(1)
            led.off()
    except OSError as e:
        led.on()
        time.sleep(1)
        print("Failed to read sensor.")
        led.off()
