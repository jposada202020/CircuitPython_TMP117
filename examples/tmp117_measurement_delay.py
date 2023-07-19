# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT

import time
import board
import tmp117

i2c = board.I2C()
tmp = tmp117.TMP117(i2c)

tmp.measurement_delay = tmp117.DELAY_8_S

delay_times = {
    0: "DELAY_0_0015_S",
    1: "DELAY_0_125_S",
    2: "DELAY_0_250_S",
    3: "DELAY_0_500_S",
    4: "DELAY_1_S",
    5: "DELAY_4_S",
    6: "DELAY_8_S",
    7: "DELAY_16_S",
}


while True:
    for measurement_delay in range(8):
        print("Current Measurement delay setting: ", delay_times[tmp.measurement_delay])
        for _ in range(10):
            print(f"Temperature: {tmp.temperature:.2f}°C")
            print()
            time.sleep(0.5)
        tmp.measurement_delay = measurement_delay
