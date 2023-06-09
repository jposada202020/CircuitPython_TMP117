# SPDX-FileCopyrightText: 2023 Jose D. Montoya
#
# SPDX-License-Identifier: Unlicense
import time
import board
import tmp117

i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller

tmp117 = tmp117.TMP117(i2c)

tmp117.high_limit = 25
tmp117.low_limit = 10

print("\nHigh limit", tmp117.high_limit)
print("Low limit", tmp117.low_limit)

# Try changing `alert_mode`  to see how it modifies the behavior of the alerts.
# tmp117.alert_mode = adafruit_tmp117.ALERT_WINDOW  #default
# tmp117.alert_mode = adafruit_tmp117.ALERT_HYSTERESIS

print("Alert mode:", tmp117.alert_mode)
print("\n\n")
while True:
    print("Temperature: %.2f degrees C" % tmp117.temperature)
    alert_status = tmp117.alert_status
    print("High alert:", alert_status.high_alert)
    print("Low alert:", alert_status.low_alert)
    print("")
    time.sleep(1)
