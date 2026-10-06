import network
import time
import json
from machine import ADC, Pin
from umqtt.simple import MQTTClient


# =========================
# CONFIGURAÇÃO WI-FI
# =========================

SSID = "A55 de Hugo"
PASSWORD = "HugoJesus"


# =========================
# CONFIGURAÇÃO MQTT
# =========================

MQTT_BROKER = "10.72.208.102"
MQTT_TOPIC = "esp32/sensores"


# =========================
# LIGAR AO WI-FI
# =========================

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)

print("A ligar ao Wi-Fi...")

while not wifi.isconnected():
    time.sleep(1)

print("Wi-Fi ligado")
print("IP:", wifi.ifconfig()[0])


# =========================
# LIGAR AO MQTT
# =========================

mqtt = MQTTClient(
    "ESP32_SENSOR",
    MQTT_BROKER,
    port=1883
)

mqtt.connect()

print("MQTT ligado")


# =========================
# SENSORES
# =========================

# LM35
lm35 = ADC(Pin(34))
lm35.atten(ADC.ATTN_11DB)

# ADXL335 - eixo X
adxl_x = ADC(Pin(35))
adxl_x.atten(ADC.ATTN_11DB)


# =========================
# CALIBRAÇÃO ADXL335
# =========================

# Tensão do eixo X quando está a 0 g
V0_X = 1.65

# Sensibilidade típica do ADXL335
SENSIBILIDADE = 0.300


# =========================
# LOOP
# =========================

while True:

    # ---------------------
    # LM35
    # ---------------------

    adc_temp = lm35.read()

    tensao_temp = adc_temp * 5 / 4095

    temperatura = tensao_temp * 100


    # ---------------------
    # ADXL335 X
    # ---------------------

    adc_x = adxl_x.read()

    tensao_x = adc_x * 3.3 / 4095

    aceleracao_x = (tensao_x - V0_X) / SENSIBILIDADE


    # ---------------------
    # JSON
    # ---------------------

    dados = {
        "temperatura": round(temperatura, 2),
        "aceleracao_x": round(aceleracao_x, 3)
    }

    mensagem = json.dumps(dados)


    # ---------------------
    # MQTT
    # ---------------------

    mqtt.publish(
        MQTT_TOPIC,
        mensagem
    )


    # ---------------------
    # MONITOR SERIAL
    # ---------------------

    print(mensagem)

    time.sleep(0.5)