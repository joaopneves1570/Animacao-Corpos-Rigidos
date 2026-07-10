import matplotlib.pyplot as plt
import numpy as np


def f(x, y):
    # Define a função implícita: x^2 + y^2 - 4 = 0
    return x**2 + y**2 - 4


# 1. Cria uma malha (grid) de pontos espalhados no intervalo de -3 a 3
x = np.linspace(-3, 3, 400)
y = np.linspace(-3, 3, 400)
X, Y = np.meshgrid(x, y)

# 2. Avalia a função implícita em cada par de coordenadas (X, Y)
Z = f(X, Y)

# 3. Configura a janela do gráfico
plt.figure(figsize=(6, 6))

# 4. Desenha a linha de contorno isolada onde Z é exatamente igual a 0
grafico = plt.contour(X, Y, Z, levels=[0], colors="forestgreen", linewidths=2)

# 5. Adiciona decorações e eixos cartesianos para referência
plt.axhline(0, color="black", linewidth=0.8, linestyle="--")
plt.axvline(0, color="black", linewidth=0.8, linestyle="--")

# 6. Configurações visuais adicionais
plt.title("Plote da Função Implícita: $x^2 + y^2 - 4 = 0$", fontsize=12)
plt.xlabel("Eixo X")
plt.ylabel("Eixo Y")
plt.grid(True, linestyle=":", alpha=0.5)

# Garante que a proporção dos eixos seja 1:1 para o círculo não ficar achatado
plt.gca().set_aspect("equal", adjustable="box")

# Exibe o gráfico na tela
plt.show()