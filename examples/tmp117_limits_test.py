# SPDX-FileCopyrightText: 2023 Jose D. Montoya
#
# SPDX-License-Identifier: Unlicense
import time
import board
import tmp117

i2c = board.I2C()  # uses board.SCL and board.SDA

tmp = tmp117.TMP117(i2c)

tmp.high_limit = 25
tmp.low_limit = 10

print("\nHigh limit", tmp.high_limit)
print("Low limit", tmp.low_limit)

# Try changing `alert_mode`  to see how it modifies the behavior of the alerts.
# tmp117.alert_mode = adafruit_tmp117.ALERT_WINDOW  #default
# tmp117.alert_mode = adafruit_tmp117.ALERT_HYSTERESIS

print("Alert mode:", tmp117.alert_mode)
print("\n\n")
while True:
    print(f"Temperature: {tmp.temperature:.2f}°C")
    print()
    alert_status = tmp117.alert_status
    print("High alert:", alert_status.high_alert)
    print("Low alert:", alert_status.low_alert)
    print("")
    time.sleep(1)
