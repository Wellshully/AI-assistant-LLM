import numpy as np
import os
import time
RESET = "\033[0m"
DONUT_COLOR = "\033[93m"  # 黃色
EYE_COLOR = "\033[96m"
screen_size = 40
theta_spacing = 0.07
phi_spacing = 0.02

illumination = np.array(list(" .:-=+*#%@"))

A = 0
B = 0
R1 = 1
R2 = 2
K2 = 5
K1 = screen_size * K2 * 3 / (8 * (R1 + R2))

def render_frame(A: float, B: float) -> np.ndarray:
    cos_A = np.cos(A)
    sin_A = np.sin(A)
    cos_B = np.cos(B)
    sin_B = np.sin(B)

    output = np.full((screen_size, screen_size), " ")
    zbuffer = np.zeros((screen_size, screen_size))

    cos_phi = np.cos(phi := np.arange(0, 2 * np.pi, phi_spacing))
    sin_phi = np.sin(phi)
    cos_theta = np.cos(theta := np.arange(0, 2 * np.pi, theta_spacing))
    sin_theta = np.sin(theta)
    circle_x = R2 + R1 * cos_theta
    circle_y = R1 * sin_theta

    x = (np.outer(cos_B * cos_phi + sin_A * sin_B * sin_phi, circle_x) - circle_y * cos_A * sin_B).T
    y = (np.outer(sin_B * cos_phi - sin_A * cos_B * sin_phi, circle_x) + circle_y * cos_A * cos_B).T
    z = ((K2 + cos_A * np.outer(sin_phi, circle_x)) + circle_y * sin_A).T
    ooz = np.reciprocal(z)
    xp = (screen_size / 2 + K1 * ooz * x).astype(int)
    yp = (screen_size / 2 - K1 * ooz * y).astype(int)
    L = (((np.outer(cos_phi, cos_theta) * sin_B - cos_A * np.outer(sin_phi, cos_theta)) - sin_A * sin_theta) +
         cos_B * (cos_A * sin_theta - np.outer(sin_phi, cos_theta * sin_A)))
    L = np.clip(np.around(L * 8), 0, len(illumination) - 1).astype(int).T

    for i in range(90):
        for j in range(315):
            if L[i, j] >= 0:
                if 0 <= xp[i, j] < screen_size and 0 <= yp[i, j] < screen_size:
                    if ooz[i, j] > zbuffer[xp[i, j], yp[i, j]]:
                        zbuffer[xp[i, j], yp[i, j]] = ooz[i, j]
                        output[xp[i, j], yp[i, j]] = DONUT_COLOR + illumination[L[i, j]] + RESET

    # 中央畫上 AI 眼睛
    eye = [
        list("⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣤⣤⣤⣤⣴⣤⣤⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀"),
        list("⠀⠀⠀⠀⠀⠀⠀⣀⣴⣾⠿⠛⠋⠉⠁⠀⠀⠀⠈⠙⠻⢷⣦⡀⠀⠀⠀⠀⠀⠀"),
        list("⠀⠀⠀⠀⠀⣤⣾⡿⠋⠁⠀⣠⣶⣿⡿⢿⣷⣦⡀⠀⠀⠀⠙⠿⣦⣀⠀⠀⠀⠀"),
        list("⠀⠀⢀⣴⣿⡿⠋⠀⠀⢀⣼⣿⣿⣿⣶⣿⣾⣽⣿⡆⠀⠀⠀⠀⢻⣿⣷⣶⣄⠀"),
        list("⠀⣴⣿⣿⠋⠀⠀⠀⠀⠸⣿⣿⣿⣿⣯⣿⣿⣿⣿⣿⠀⠀⠀⠐⡄⡌⢻⣿⣿⡷"),
        list("⢸⣿⣿⠃⢂⡋⠄⠀⠀⠀⢿⣿⣿⣿⣿⣿⣯⣿⣿⠏⠀⠀⠀⠀⢦⣷⣿⠿⠛⠁"),
        list("⠀⠙⠿⢾⣤⡈⠙⠂⢤⢀⠀⠙⠿⢿⣿⣿⡿⠟⠁⠀⣀⣀⣤⣶⠟⠋⠁⠀⠀⠀"),
        list("⠀⠀⠀⠀⠈⠙⠿⣾⣠⣆⣅⣀⣠⣄⣤⣴⣶⣾⣽⢿⠿⠟⠋⠀⠀⠀⠀⠀⠀⠀"),
        list("⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠙⠛⠛⠙⠋⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀")
    ]
    ex, ey = len(eye), len(eye[0])
    ox = screen_size // 2 - ex // 2
    oy = screen_size // 2 - ey // 2
    for i in range(ex):
        for j in range(ey):
            char = eye[i][j]
            if char != "⠀":  # 全形空白 U+2800
                if 0 <= ox + i < screen_size and 0 <= oy + j < screen_size:
                    output[ox + i, oy + j] = EYE_COLOR + char + RESET

    return output

def pprint(array: np.ndarray) -> None:
    os.system("cls" if os.name == "nt" else "clear")
    print("\n".join("".join(row) for row in array))

if __name__ == "__main__":
    try:
        while True:
            A += theta_spacing
            B += phi_spacing
            frame = render_frame(A, B)
            pprint(frame)
            time.sleep(0.03)
    except KeyboardInterrupt:
        print("\n[❎ 停止旋轉]")