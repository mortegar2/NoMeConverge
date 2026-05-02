#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Prueba rápida de bisección para verificar historial."""

from src.algoritmos.raices import biseccion

# Prueba de bisección
f = lambda x: x**3 - x - 2
res = biseccion(f, 1, 2, tol=1e-3, max_iter=20)

print('=== BISECCIÓN ===')
print(f'Raíz encontrada: {res["raiz"]:.6f}')
print(f'Iteraciones: {res["iteraciones"]}')
print(f'Error final: {res["error"]:.6e}')
print(f'\nPrimer detalle del historial:')
print(res['historial'][0]['detalle'])
print(f'\nÚltimo detalle del historial:')
print(res['historial'][-1]['detalle'])
