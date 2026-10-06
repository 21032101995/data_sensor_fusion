import network
import time
import json
from machine import ADC, Pin
from umqtt.simple import MQTTClient


class wifi_connection:
    def __init__(self, ssid, password):
        self.wifi = network.WLAN(network.STA_IF)
        self.ssid = ssid
        self.password = password

    def connect(self):
        self.wifi.active(True)
        self.wifi.connect(self.ssid, self.password)
        print("A ligar ao Wi-Fi...")

        while not self.wifi.isconnected():
            time.sleep(1)

        print("Wi-Fi ligado")
        print("IP:", self.wifi.ifconfig()[0])


class mqtt_connection:
    def __init__(self, broker_ip, port, topic, client_id="esp32_client"):
        self.broker_ip = broker_ip
        self.port = port
        self.topic = topic
        # MQTTClient takes client_id as the first argument
        self.mqtt = MQTTClient(client_id, self.broker_ip, port=self.port)

    def connect(self):
        self.mqtt.connect()
        print("MQTT ligado")

    def publish(self, message):
        self.mqtt.publish(self.topic, message)


class config_ADC:
    def __init__(self, number):
        self.pin_number = number
        self.measurement = ADC(Pin(self.pin_number))
        self.measurement.atten(ADC.ATTN_11DB)  # Configure 0-3.3V range for ESP32

    def read_values(self):
        if self.pin_number == 34:
            temperature = self.read_temperature(self.measurement)
            return temperature
        elif self.pin_number == 35:
            acc_x = self.read_aceleration_x(self.measurement)
            return acc_x
        else:
            print("Pino não configurado")
            return 0

    def read_temperature(self, measurement):
        bin_value = measurement.read()
        voltage = bin_value * 5 / 4095  # Standard ESP32 voltage scaling (3.3V max)
        temperature = voltage * 100
        return temperature

    def read_aceleration_x(self, measurement):
        adc_x = measurement.read()
        tensao_x = adc_x * 3.3 / 4095
        SENSIBILIDADE = 0.300
        V0_X = 1.65  # Zero-g voltage baseline (typically VCC/2 = 3.3V / 2)
        aceleration_x = (tensao_x - V0_X) / SENSIBILIDADE
        return aceleration_x


def sensor_fusion(temperature, aceleration_x):
    data = {
        "temperatura": round(temperature, 2),
        "aceleracao_x": round(aceleration_x, 3),
    }
    return json.dumps(data)


def main_process():
    # Wi-Fi Setup
    credentials = wifi_connection("Deco", "45295199")
    credentials.connect()

    # MQTT Setup
    mqtt_conn = mqtt_connection("192.168.68.103", 1883, "esp32/sensors")
    mqtt_conn.connect()

    # ADC Setup
    temp_ch = config_ADC(34)
    accx_ch = config_ADC(35)

    while True:
        temp = temp_ch.read_values()
        accx = accx_ch.read_values()

        message = sensor_fusion(temp, accx)
        mqtt_conn.publish(message)
        print("Enviado:", message)

        time.sleep(1)  # Delay between reads


if __name__ == "__main__":
    main_process()