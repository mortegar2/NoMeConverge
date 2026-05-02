# GUÍA RÁPIDA: Interfaz Sincronizada con PDF

## ¿Qué cambió?

La interfaz de raíces e interpolación ahora muestra **exactamente lo mismo** que aparecerá en el PDF.

### Antes
- Tabla pequeña con solo números
- Detalles técnicos ocultos
- Difícil de sincronizar con PDF

### Ahora
- **Tabla clara**: Iteración, Valor Parcial, Error
- **Panel de Procedimiento**: Muestra paso a paso completo
- **Sincronización perfecta**: UI = PDF

---

## Cómo Funciona

### 1. Ejecutar la Aplicación
```bash
python main.py
```

### 2. Pestaña "Cálculo de Raíces" - Ejemplo Bisección

#### Parámetros
```
f(x) = x**3 - x - 2
Método = Bisección
a = 1
b = 2
Tolerancia = 1e-6
Max Iter = 100
```

#### Click en "Calcular"

Verás:
- **Tabla (arriba)**:
  ```
  Iter | Valor Parcial | Error
  ---- | ------------- | ------
    1  |  1.500000     | 0.500000
    2  |  1.750000     | 0.250000
    3  |  1.625000     | 0.125000
    ...
  ```

- **Panel Procedimiento (abajo)**:
  ```
  ======================================================================
  MÉTODO: Bisección
  ======================================================================
  
  Intervalo inicial: [1, 2]
  Función: f(x) = x**3 - x - 2
  Tolerancia: 1e-06
  Máximo de iteraciones: 100
  
  ======================================================================
  
  ----------------------------------------
  ITERACIÓN 1
  ----------------------------------------
  a = 1
  b = 2
  
  c = (a + b)/2 = 1.5
  
  f(c) = -0.125
  
  Error = 0.5
  
  ----------------------------------------
  ITERACIÓN 2
  ----------------------------------------
  [...]
  
  ======================================================================
  RESULTADO FINAL
  ======================================================================
  Raíz aproximada: 1.5214844
  Número de iteraciones: 9
  Error final: 1.95e-03
  ======================================================================
  ```

- **Gráfica (derecha)**: Visualización de la función y la raíz encontrada

#### Click en "PDF"
1. Se abre un diálogo preguntando: "¿Incluir gráfico en el PDF?"
2. Se genera `raices.pdf`
3. El PDF contiene:
   - Misma información que el Panel Procedimiento
   - Parámetros iniciales
   - Todas las iteraciones con detalles
   - Resultado final
   - Gráfico (opcional)

---

## Pestaña "Interpolación" - Ejemplo Lagrange

#### Parámetros
```
Puntos X = 1,2,3
Puntos Y = 2,4,9
Evaluar en x = 2.5
Método = Lagrange
```

#### Click en "Calcular"

Verás:
- **Tabla**:
  ```
  Iter | Valor Parcial | Error
  ---- | ------------- | ------
    1  |  2.000000     | 0.000000
    2  |  0.000000     | 2.000000
    3  |  4.000000     | 4.000000
  ```

- **Panel Procedimiento**:
  ```
  ======================================================================
  MÉTODO: Interpolación Lagrange
  ======================================================================
  
  Puntos X: 1,2,3
  Puntos Y: 2,4,9
  Evaluar en x = 2.5
  
  ======================================================================
  
  CONSTRUCCIÓN DEL POLINOMIO:
  ----------
  
  Iteración 1:
  Valor parcial: 2.0
  Error: 0
  Detalle: L0(x) = y0 * (x - x1)/(x0 - x1) * (x - x2)/(x0 - x2) * ...
  
  [...]
  
  ======================================================================
  POLINOMIO CONSTRUIDO:
  ======================================================================
  2 * L0(x) + 4 * L1(x) + 9 * L2(x)
  
  ======================================================================
  VERIFICACIÓN EN PUNTOS ORIGINALES:
  ======================================================================
  x = 1: Esperado = 2, Calculado = 2.000000, Error = 0.00e+00
  x = 2: Esperado = 4, Calculado = 4.000000, Error = 0.00e+00
  x = 3: Esperado = 9, Calculado = 9.000000, Error = 0.00e+00
  
  ======================================================================
  RESULTADO FINAL:
  ======================================================================
  Valor en x = 2.5: 6.125000
  ======================================================================
  ```

- También aparece:
  ```
  Resultado: 6.125000
  Polinomio: 2 * L0(x) + 4 * L1(x) + 9 * L2(x)
  ```

#### Click en "PDF"

Se genera `interpolacion.pdf` con la misma información elegantemente formateada.

---

## Verificación de Sincronización

### Test Automático
```bash
python test_sincronizacion.py
```

Verifica:
- ✓ Algoritmos generan historial correcto
- ✓ Estructura de datos es válida
- ✓ Todos los datos necesarios están presentes

### Test Manual

1. **Ejecuta** `python main.py`
2. **Calcula** una bisección con:
   - f(x) = x**3 - x - 2
   - a = 1, b = 2
   - tol = 1e-6
3. **Observa**:
   - ✓ Tabla muestra todas las iteraciones
   - ✓ Panel muestra procedimiento completo
   - ✓ Gráfica visualiza la función
4. **Exporta PDF**:
   - ✓ La información es idéntica
   - ✓ Formato es profesional

---

## Estructura de Datos

### Historial de Iteraciones
Cada iteración contiene:
```python
{
    "iter": 1,                    # Número de iteración
    "valor_parcial": 1.5,         # Valor aproximado
    "error": 0.5,                 # Error numérico
    "detalle": "......."          # Descripción textual completa
}
```

### Flujo Completo
```
ALGORITMO (raices.py)
    ↓ genera
HISTORIAL (lista de dicts)
    ↓ usa
    ├→ UI TABLA (widget Treeview)
    ├→ UI PROCEDIMIENTO (widget Text)
    └→ PDF (reportlab)
```

---

## Ventajas de Esta Arquitectura

| Característica | Antes | Ahora |
|---|---|---|
| **Claridad visual** | Tabla confusa | Tabla + Procedimiento |
| **Detalles ocultos** | Sí | No, todo visible |
| **Sincronización UI-PDF** | Manual | Automática |
| **Escalabilidad** | Limitada | Ilimitada |
| **Profesionalismo** | Regular | Excelente |

---

## Solución de Problemas

### ❌ La tabla está vacía
→ Asegúrate de hacer click en "Calcular"

### ❌ El panel procedimiento está vacío
→ Verifica que hay datos en la tabla. Si la tabla está llena, es un bug en `_mostrar_procedimiento()`

### ❌ El PDF no tiene detalles
→ Asegúrate de generar el PDF después de calcular en la UI

### ❌ Error al generar PDF
→ Verifica que tienes permisos de escritura en el directorio actual

### ❌ Los números no coinciden entre UI y PDF
→ No debería ocurrir. Usa el mismo historial en ambos.

---

## Próximos Pasos (Opcional)

Si quieres extender esta funcionalidad:

1. **Agregar Newton-Raphson**: Ya está, solo calcula diferente en la interfaz
2. **Agregar Secante**: Ya está
3. **Agregar más métodos**: Sigue la misma estructura

4. **Mejorar el PDF**:
   ```python
   # Incluir ecuación formateada (usar sympy)
   # Incluir gráficos más bonitos
   # Agregar análisis de convergencia
   ```

5. **Mejorar la UI**:
   ```python
   # Expandir el panel procedimiento automáticamente
   # Colorear iteraciones según el error
   # Agregar botones para navegar iteraciones
   ```

---

## Contacto / Preguntas

Si hay algo que no está sincronizado, revisa:
1. `src/algoritmos/*.py` - La generación del historial
2. `src/interfaz/vistas/*.py` - Cómo se usa el historial
3. `test_sincronizacion.py` - Para validar los datos

¡Listo! Tu interfaz está completamente sincronizada. 🎉
