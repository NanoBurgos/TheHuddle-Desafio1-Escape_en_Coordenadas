import tkinter as tk
from tkinter import messagebox
import random

# Tamaño de cada celda
tamano_celda_px = 40

# Variables globales
tablero = []
inicio = (0, 0)
meta = (0, 0)
numero_filas = 10
numero_columnas = 10

ventana = tk.Tk()
ventana.title("Escape de Coordenadas - Luciano Burgos")

# Cosas para Tkinter, etiquetas
label_filas = tk.Label(ventana, text="Filas:")
label_filas.grid(row=0, column=0)
entry_filas = tk.Entry(ventana)
entry_filas.insert(0, "10")
entry_filas.grid(row=0, column=1)

label_columnas = tk.Label(ventana, text="Columnas:")
label_columnas.grid(row=0, column=2)
entry_columnas = tk.Entry(ventana)
entry_columnas.insert(0, "10")
entry_columnas.grid(row=0, column=3)

label_inicio = tk.Label(ventana, text="Inicio (fila,col):")
label_inicio.grid(row=1, column=0)
entry_inicio = tk.Entry(ventana)
entry_inicio.insert(0, "0,0")
entry_inicio.grid(row=1, column=1)

label_meta = tk.Label(ventana, text="Meta (fila,col):")
label_meta.grid(row=1, column=2)
entry_meta = tk.Entry(ventana)
entry_meta.insert(0, "9,9")
entry_meta.grid(row=1, column=3)

boton_crear = tk.Button(ventana, text="Crear mapa")
boton_crear.grid(row=2, column=0, columnspan=4)

label_info = tk.Label(
    ventana,
    text="Clic en las celdas para cambiar terreno:\n0=Libre, 1=Edificio, 2=Agua, 3=Bloque temporal (desaparece en 5s)"
)
label_info.grid(row=3, column=0, columnspan=4)

canvas = tk.Canvas(ventana, width=400, height=400, bg="white")
canvas.grid(row=4, column=0, columnspan=4)

# FUNCIONES  

def celda_valida(fila, columna):
    return 0 <= fila < numero_filas and 0 <= columna < numero_columnas

def dibujar_tablero(ruta=None):
    canvas.delete("all")
    colores = {0: "white", 1: "black", 2: "aqua", 3: "orange"}

    for fila in range(numero_filas):
        for columna in range(numero_columnas):
            color = colores[tablero[fila][columna]]
            x1, y1 = columna * tamano_celda_px, fila * tamano_celda_px
            x2, y2 = x1 + tamano_celda_px, y1 + tamano_celda_px
            canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")

    # inicio y meta
    x1, y1 = inicio[1] * tamano_celda_px, inicio[0] * tamano_celda_px
    canvas.create_rectangle(x1, y1, x1 + tamano_celda_px, y1 + tamano_celda_px, fill="green")

    x1, y1 = meta[1] * tamano_celda_px, meta[0] * tamano_celda_px
    canvas.create_rectangle(x1, y1, x1 + tamano_celda_px, y1 + tamano_celda_px, fill="red")

    if ruta:
        for fila, columna in ruta:
            if (fila, columna) in [inicio, meta]:
                continue
            x1, y1 = columna * tamano_celda_px, fila * tamano_celda_px
            canvas.create_rectangle(x1, y1, x1 + tamano_celda_px, y1 + tamano_celda_px, fill="blue")

def vecinos(fila, columna):
    posibles = [(fila-1,columna),(fila+1,columna),(fila,columna-1),(fila,columna+1)]
    return [(f,c) for f,c in posibles if celda_valida(f,c) and tablero[f][c] != 1]

def heuristica(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def ejecutar_a_estrella():
    abiertos = [inicio]
    camino_previo = {}
    costos = [[float("inf")] * numero_columnas for _ in range(numero_filas)]
    puntajes = [[float("inf")] * numero_columnas for _ in range(numero_filas)]

    costos[inicio[0]][inicio[1]] = 0
    puntajes[inicio[0]][inicio[1]] = heuristica(inicio, meta)

    while abiertos:
        abiertos.sort(key=lambda cel: puntajes[cel[0]][cel[1]])
        actual = abiertos.pop(0)

        if actual == meta:
            ruta = [meta]
            while ruta[-1] in camino_previo:
                ruta.append(camino_previo[ruta[-1]])
            dibujar_tablero(ruta)
            return

        for f, c in vecinos(*actual):
            costo_mov = 1
            if tablero[f][c] == 2: costo_mov = 2
            elif tablero[f][c] == 3: costo_mov = 5

            nuevo_costo = costos[actual[0]][actual[1]] + costo_mov
            if nuevo_costo < costos[f][c]:
                costos[f][c] = nuevo_costo
                puntajes[f][c] = nuevo_costo + heuristica((f, c), meta)
                camino_previo[(f, c)] = actual
                if (f, c) not in abiertos:
                    abiertos.append((f, c))

    messagebox.showinfo("Ruta", "No hay ruta posible")

def click_celda(evento):
    columna = evento.x // tamano_celda_px
    fila = evento.y // tamano_celda_px

    if not celda_valida(fila, columna):
        return
    if (fila, columna) in [inicio, meta]:
        return

    tablero[fila][columna] = (tablero[fila][columna] + 1) % 4

    # Si es bloque temporal, eliminar en 5s (para que sea como un auto que esta en una ubicacion pero luego se va, y deja libre el camino)
    if tablero[fila][columna] == 3:
        ventana.after(5000, lambda f=fila, c=columna: limpiar_bloque_temporal(f, c))

    ejecutar_a_estrella()

def limpiar_bloque_temporal(fila, columna):
    if tablero[fila][columna] == 3:  
        tablero[fila][columna] = 0
        ejecutar_a_estrella()

def generar_obstaculos_aleatorios():
    tipos = [1, 2, 3]
    for fila in range(numero_filas):
        for columna in range(numero_columnas):
            if (fila, columna) in [inicio, meta]:
                continue
            if random.random() < 0.2:
                tablero[fila][columna] = random.choice(tipos)
                if tablero[fila][columna] == 3:
                    ventana.after(5000, lambda f=fila, c=columna: limpiar_bloque_temporal(f, c))

def crear_mapa():
    global numero_filas, numero_columnas, tablero, inicio, meta

    numero_filas = int(entry_filas.get())
    numero_columnas = int(entry_columnas.get())

    canvas.config(width=numero_columnas*tamano_celda_px, height=numero_filas*tamano_celda_px)

    tablero = [[0 for _ in range(numero_columnas)] for _ in range(numero_filas)]

    try:
        inicio = tuple(map(int, entry_inicio.get().split(",")))
        meta = tuple(map(int, entry_meta.get().split(",")))
    except:
        messagebox.showerror("Error", "Coordenadas inválidas")
        return

    if not (celda_valida(*inicio) and celda_valida(*meta)):
        messagebox.showerror("Error", "Inicio o meta fuera del mapa")
        return

    generar_obstaculos_aleatorios()
    ejecutar_a_estrella()

# ENLACES para Tkinter
boton_crear.config(command=crear_mapa)
canvas.bind("<Button-1>", click_celda)

ventana.mainloop()
