# Identify valid phases (those not missing)

# missing_phases = [18, 21, 30, 31, 34, 35,47]
# valid_phases=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 19, 20, 22, 23, 24, 25, 26, 27, 28, 29, 32, 33, 36, 37, 38, 39, 40,41,42,43,44,45,47]
import numpy as np
miss_ph=[2,4]

a_obtained = np.array( [[1,     2,   3,    4   ],
                          [5,     6,   7,    8   ],
                          [9,    10,   11,  12   ],
                          [13,   14,   15,   16  ],
                          [17,   18,    19,   20  ],
                          [21,   22,    23,   24    ]])
for i in range(2):
  desired_cols_ids = np.array([miss_ph[i]], dtype=np.int64)
  zero_arr_row = np.zeros((1, a_obtained.shape[1]))
  a_obtained = np.insert(a_obtained, desired_cols_ids, zero_arr_row, axis=0)
  zero_arr_col = np.zeros((a_obtained.shape[0], 1))
  a_obtained = np.insert(a_obtained, desired_cols_ids, zero_arr_col, axis=1)
  print(a_obtained)
