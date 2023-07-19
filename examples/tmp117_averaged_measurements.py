# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT

import time
import board
import tmp117

i2c = board.I2C()
tmp = tmp117.TMP117(i2c)

tmp.averaged_measurements = tmp117.AVERAGE_1X

while True:
    for averaged_measurements in tmp117.averaged_measurements_values:
        print("Current Averaged measurements setting: ", tmp.averaged_measurements)
        for _ in range(10):
            print(f"Temperature: {tmp.temperature:.2f}°C")
            print()
            time.sleep(0.5)
        tmp.averaged_measurements = averaged_measurements
