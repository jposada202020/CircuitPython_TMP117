# SPDX-FileCopyrightText: 2023 Jose D. Montoya
#
# SPDX-License-Identifier: Unlicense
import time
import board
import tmp117

# i2c = board.I2C()  # uses board.SCL and board.SDA
i2c = (
    board.STEMMA_I2C()
)  # For using the built-in STEMMA QT connector on a microcontroller

tmp = tmp117.TMP117(i2c)

print("Temperature without offset: ", tmp.temperature)
tmp117.temperature_offset = 10.0
while True:
    print(f"Temperature with offset: {tmp.temperature:.2f}°C")
    print()
    time.sleep(1)
