# Sistema de Predicción de Heladas con Inteligencia Artificial
## Guía de Presentación para Congreso Internacional

---

## Tabla de Contenidos

1. [Resumen Ejecutivo](#1-resumen-ejecutivo)
2. [El Desafío Agrícola](#2-el-desafío-agrícola)
3. [Descripción General del Sistema](#3-descripción-general-del-sistema)
4. [Arquitectura del Sistema](#4-arquitectura-del-sistema)
5. [Recolección de Datos e Integración IoT](#5-recolección-de-datos-e-integración-iot)
6. [Algoritmos de Aprendizaje Automático](#6-algoritmos-de-aprendizaje-automático)
7. [Flujo de Trabajo de Predicción](#7-flujo-de-trabajo-de-predicción)
8. [Reglas de Decisión y Sistema de Alertas](#8-reglas-de-decisión-y-sistema-de-alertas)
9. [Automatización y Programación](#9-automatización-y-programación)
10. [Stack Técnico](#10-stack-técnico)
11. [Implementación en el Mundo Real](#11-implementación-en-el-mundo-real)
12. [Resultados e Impacto](#12-resultados-e-impacto)
13. [Mejoras Futuras](#13-mejoras-futuras)
14. [Conclusión](#14-conclusión)

---

## 1. Resumen Ejecutivo

Este proyecto presenta un **sistema de predicción de heladas impulsado por inteligencia artificial** que combina tecnología de sensores IoT con algoritmos avanzados de aprendizaje automático para proporcionar alertas tempranas de heladas a los agricultores. El sistema integra datos meteorológicos en tiempo real de la red IoT The Things Stack (TTS) y emplea un enfoque híbrido de aprendizaje automático que combina modelos SARIMA y LSTM para predecir condiciones de heladas con alta precisión.

**Características Clave:**
- Recolección de datos en tiempo real de sensores IoT (temperatura, humedad, velocidad del viento)
- Modelos duales de aprendizaje automático (SARIMA + LSTM) con fusión híbrida
- Predicciones diarias automatizadas (3:00 AM, 12:00 PM, 4:00 PM)
- Notificaciones por WhatsApp a agricultores a las 5:00 PM diarias
- Diseño de Arquitectura Limpia para escalabilidad y mantenibilidad

---

## 2. El Desafío Agrícola

### Planteamiento del Problema

Las heladas son uno de los fenómenos climáticos más devastadores para la agricultura, causando:
- **Daño y pérdida de cultivos**: Las temperaturas bajo cero destruyen las células vegetales
- **Impacto económico**: Pérdidas financieras significativas para los agricultores
- **Preocupaciones de seguridad alimentaria**: Rendimientos reducidos afectan el suministro de alimentos
- **Tiempo de advertencia limitado**: Los pronósticos tradicionales carecen de precisión para microclimas

### Por Qué Esto Importa

Los agricultores necesitan:
- **Predicciones precisas**: Saber cuándo ocurrirán las heladas con alta confianza
- **Alertas oportunas**: Tiempo suficiente para implementar medidas de protección
- **Información accionable**: Orientación clara sobre los niveles de riesgo
- **Tecnología accesible**: Sistema fácil de usar sin barreras técnicas

---

## 3. Descripción General del Sistema

### Qué Hace

El sistema proporciona predicciones automáticas de heladas mediante:
1. **Recolectando** datos meteorológicos en tiempo real de sensores IoT
2. **Analizando** patrones históricos usando aprendizaje automático
3. **Prediciendo** probabilidad de heladas para las próximas 12-24 horas
4. **Notificando** a los agricultores vía WhatsApp con alertas accionables

### Cómo Funciona

```
Sensores IoT → Recolección de Datos → Modelos ML → Predicción → Alerta WhatsApp
   (TTS)       (Cada 5 min)          (SARIMA+LSTM)  (3x diarias)   (5:00 PM)
```

### Componentes Principales

1. **Capa de Datos**: Sensores IoT + integración con The Things Stack
2. **Capa de Inteligencia**: Modelos de aprendizaje automático SARIMA + LSTM
3. **Capa de Aplicación**: Backend FastAPI con programación automatizada
4. **Capa de Notificación**: Servicio de mensajería WhatsApp de Twilio

---

## 4. Arquitectura del Sistema

### Arquitectura Limpia (Arquitectura de Cebolla)

El sistema sigue los principios de **Arquitectura Limpia** con clara separación de responsabilidades:

```
┌─────────────────────────────────────────────────────┐
│          Capa de Interfaces (API)                    │
│     Controladores FastAPI, Esquemas, Middleware     │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│       Capa de Aplicación (Casos de Uso)             │
│    Generación de Predicciones, Envío de Alertas     │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│        Capa de Dominio (Lógica de Negocio)          │
│   Entidades, Repositorios, Interfaces de Servicios  │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│    Capa de Infraestructura (Servicios Externos)     │
│   Cliente TTS, Modelos ML, Twilio, Base de Datos    │
└─────────────────────────────────────────────────────┘
```

### Beneficios de Esta Arquitectura

- **Modularidad**: Cada capa tiene una única responsabilidad
- **Testeabilidad**: Lógica de negocio independiente de servicios externos
- **Mantenibilidad**: Fácil actualizar o reemplazar componentes
- **Escalabilidad**: Se pueden agregar nuevos modelos o canales de notificación fácilmente
- **Inversión de Dependencias**: La lógica central no depende de frameworks

---

## 5. Recolección de Datos e Integración IoT

### Integración con The Things Stack (TTS)

**The Things Stack** es un servidor de red LoRaWAN que gestiona dispositivos sensores IoT.

#### Fuentes de Datos

El sistema recolecta tres parámetros meteorológicos críticos:
- **Temperatura (°C)**: Indicador principal de riesgo de heladas
- **Humedad (%)**: Afecta el punto de rocío y la formación de heladas
- **Velocidad del Viento (m/s)**: El viento reduce la probabilidad de heladas

#### Proceso de Recolección de Datos

1. **Transmisión de Sensores**: Los sensores IoT transmiten datos cada 5 minutos vía LoRaWAN
2. **Recepción TTS**: The Things Stack recibe y almacena los datos de los sensores
3. **Integración API**: El backend obtiene datos vía API de Almacenamiento de TTS
4. **Procesamiento de Datos**: Los datos crudos se limpian, validan y almacenan
5. **Actualizaciones Continuas**: El sistema mantiene una ventana móvil de 10 días de datos

#### Integración API de TTS

```python
# Estructura del Endpoint
GET /api/v3/as/applications/{application_id}/packages/storage/{storage_id}/uplink_message

# Parámetros
- field_mask: Especifica qué campos devolver
- after: Timestamp de inicio (ISO 8601)
- before: Timestamp de fin (ISO 8601)
- limit: Máximo de registros (hasta 10,000)
```

#### Calidad de Datos

- **Remuestreo**: Datos remuestreados a intervalos consistentes de 5 minutos
- **Interpolación**: Valores faltantes interpolados de puntos vecinos
- **Validación**: Valores atípicos y lecturas inválidas filtradas
- **Timestamp**: Todos los datos con marca de tiempo en UTC para consistencia

---

## 6. Algoritmos de Aprendizaje Automático

El sistema emplea un **enfoque híbrido** combinando dos modelos complementarios de aprendizaje automático:

### 6.1 Modelo SARIMA (Seasonal AutoRegressive Integrated Moving Average)

#### Qué Es

SARIMA es un modelo clásico de **pronóstico de series temporales** que captura patrones estacionales y tendencias en datos de temperatura.

#### Configuración

```
SARIMA(0,0,1)(0,1,2,144)
```

**Parámetros Explicados:**
- **No estacional**: (p=0, d=0, q=1)
  - p=0: Sin términos autoregresivos
  - d=0: Sin diferenciación necesaria
  - q=1: Un término de media móvil
- **Estacional**: (P=0, D=1, Q=2, m=144)
  - P=0: Sin términos autoregresivos estacionales
  - D=1: Diferenciación estacional de primer orden
  - Q=2: Dos términos de media móvil estacional
  - m=144: Período estacional (24 horas × 6 intervalos/hora = 144 intervalos de cinco minutos)

#### Cómo Funciona

1. **Preparación de Datos**:
   - Usa 10 días de datos históricos de temperatura
   - Remuestrea a intervalos de 5 minutos (288 puntos/día)
   - Total de ~2,880 puntos de datos

2. **Entrenamiento del Modelo**:
   - Ajusta el modelo SARIMAX a la serie de temperatura
   - Captura ciclos diarios de temperatura (patrones diurnos)
   - Identifica patrones estacionales (variaciones de temperatura día/noche)

3. **Predicción**:
   - Pronostica los próximos 12 intervalos (1 hora adelante)
   - Extrae la temperatura mínima pronosticada
   - Convierte temperatura a probabilidad de helada

#### Cálculo de Probabilidad

```python
if min_temp <= 0°C:
    probability = min(0.9, max(0.7, (2 - min_temp) / 4))
elif min_temp <= 4°C:
    probability = 0.3 + (4 - min_temp) * 0.1
else:
    probability = max(0.05, 0.3 - (min_temp - 4) * 0.05)
```

**Lógica:**
- Por debajo de 0°C: 70-90% de probabilidad (alto riesgo)
- 0-4°C: 30-70% de probabilidad (riesgo moderado)
- Por encima de 4°C: 5-30% de probabilidad (bajo riesgo)

#### Fortalezas

- Excelente para capturar **patrones temporales**
- Comprende **ciclos estacionales** (variaciones diarias de temperatura)
- Computacionalmente eficiente (se ajusta en 20-40 segundos)
- Metodología interpretable y bien establecida

#### Limitaciones

- Solo usa temperatura (univariable)
- Asume que los patrones continúan (tiene dificultades con cambios repentinos)
- Solo relaciones lineales

---

### 6.2 Modelo LSTM (Long Short-Term Memory Neural Network)

#### Qué Es

LSTM es un tipo de **red neuronal recurrente** (RNN) que puede aprender patrones complejos de datos secuenciales usando múltiples características.

#### Arquitectura

```python
Sequential([
    LSTM(50 unidades, return_sequences=True, regularización L2)
    Dropout(0.3)
    LSTM(50 unidades, return_sequences=False, regularización L2)
    Dropout(0.3)
    Dense(25 unidades, activación ReLU, regularización L2)
    Dropout(0.2)
    Dense(1 unidad, activación Sigmoid)
])
```

**Desglose de Capas:**
1. **Primera Capa LSTM**: 50 unidades, procesa secuencias y pasa a la siguiente capa
2. **Dropout 30%**: Previene sobreajuste eliminando conexiones aleatoriamente
3. **Segunda Capa LSTM**: 50 unidades, produce el estado oculto final
4. **Dropout 30%**: Regularización adicional
5. **Capa Densa**: 25 unidades con activación ReLU para no linealidad
6. **Dropout 20%**: Regularización final
7. **Capa de Salida**: Una sola unidad con sigmoid (salida 0-1 probabilidad)

#### Características de Entrada (Multivariable)

El modelo LSTM usa **tres parámetros meteorológicos**:
1. **Temperatura (°C)**
2. **Humedad (%)**
3. **Velocidad del Viento (m/s)**

#### Longitud de Secuencia

- **144 pasos de tiempo** = 12 horas de intervalos de 5 minutos
- El modelo observa 12 horas de datos históricos para predecir la próxima hora

#### Cómo Funciona

1. **Preparación de Datos**:
   - Crea secuencias de 144 pasos de tiempo (12 horas)
   - Cada paso de tiempo contiene [temperatura, humedad, velocidad_viento]
   - Datos escalados usando MinMaxScaler (rango 0-1)

2. **Creación de Objetivo**:
   - Para cada secuencia, mira adelante 12 intervalos (1 hora)
   - Calcula temperatura mínima en la próxima hora
   - Convierte a probabilidad continua de helada (0.0-1.0)

3. **Entrenamiento**:
   - 50 épocas con parada temprana (patience=10)
   - Tamaño de lote: 32
   - División de validación: 20%
   - Optimizador: Adam (learning_rate=0.001)
   - Función de pérdida: MSE (Error Cuadrático Medio)
   - Métrica: MAE (Error Absoluto Medio)

4. **Predicción**:
   - Toma las últimas 12 horas de datos
   - Las pasa por la red entrenada
   - Produce probabilidad de helada (0.0-1.0)

#### Fórmula de Objetivo de Probabilidad

```python
if min_temp <= 0°C:
    frost_prob = min(0.9, max(0.7, (2 - min_temp) / 4))
elif min_temp <= 4°C:
    frost_prob = 0.3 + (4 - min_temp) * 0.1  # 0.3 a 0.7
else:
    frost_prob = max(0.05, 0.3 - (min_temp - 4) * 0.05)
```

#### Técnicas de Regularización

- **Regularización L2**: Penaliza pesos grandes (0.001)
- **Dropout**: Elimina neuronas aleatoriamente durante el entrenamiento
- **Parada Temprana**: Se detiene si la pérdida de validación no mejora por 10 épocas

#### Fortalezas

- **Multivariable**: Usa temperatura, humedad y velocidad del viento
- **Patrones no lineales**: Captura relaciones complejas
- **Dependencias temporales**: Entiende patrones a largo plazo (12 horas)
- **Adaptativo**: Aprende de los datos sin programación explícita

#### Limitaciones

- Requiere tiempo sustancial de entrenamiento (2-3 minutos con 50 épocas)
- Más costoso computacionalmente que SARIMA
- Naturaleza de "caja negra" (menos interpretable)
- Necesita datos suficientes para entrenamiento

---

### 6.3 Modelo de Fusión Híbrida

#### ¿Por Qué Híbrido?

**Combinar SARIMA y LSTM aprovecha las fortalezas de ambos:**

| Modelo | Fortalezas | Debilidades |
|--------|-----------|-------------|
| SARIMA | Rápido, interpretable, bueno en patrones estacionales | Univariable, lineal |
| LSTM | Multivariable, captura patrones complejos | Lento, menos interpretable |
| **HÍBRIDO** | **Lo mejor de ambos mundos** | **Mínimas** |

#### Fórmula de Fusión

```python
hybrid_probability = (sarima_probability × 0.4) + (lstm_probability × 0.6)
```

**Promedio ponderado** con LSTM recibiendo mayor peso (60%) y SARIMA 40%.

#### ¿Por Qué Estos Pesos?

- **Fortaleza LSTM (60%)**: El enfoque multivariable captura interacciones complejas entre temperatura, humedad y viento
- **Complemento SARIMA (40%)**: Proporciona validación de patrones temporales y consistencia estacional
- **Robustez**: Si un modelo tiene una salida inusual, el otro compensa
- **Rendimiento**: El enfoque ponderado da más influencia al modelo más sofisticado

#### Ejemplo de Cálculo

```
Escenario: Prediciendo helada para esta noche

Modelo SARIMA:
- Temp. mín. pronosticada: 1°C
- Probabilidad: 0.65 (65%)

Modelo LSTM:
- Temperatura: 2°C, Humedad: 85%, Viento: 0.5 m/s
- Probabilidad: 0.72 (72%)

Fusión Híbrida:
- (0.65 × 0.4) + (0.72 × 0.6) = 0.692
- Probabilidad Final: 69.2%
```

#### Beneficios del Enfoque Híbrido

1. **Precisión Mejorada**: Reduce errores de modelos individuales
2. **Robustez**: Menos sensible a valores atípicos o debilidades específicas del modelo
3. **Confianza**: El consenso entre modelos aumenta la confiabilidad
4. **Complementariedad**: SARIMA captura patrones temporales, LSTM captura relaciones multivariables

---

### 6.4 Resumen Comparativo de Modelos

| Aspecto | SARIMA | LSTM | Híbrido |
|---------|--------|------|---------|
| **Características de Entrada** | Solo temperatura | Temp + Humedad + Viento | Ambos |
| **Tiempo de Entrenamiento** | 20-40 segundos | 2-3 minutos | Combinado |
| **Horizonte de Pronóstico** | 1 hora (12 intervalos) | 1 hora (12 intervalos) | 1 hora |
| **Datos Requeridos** | Mínimo 10 días | Mínimo 10 días | Mínimo 10 días |
| **Tipo de Patrón** | Lineal, estacional | No lineal, complejo | Ambos |
| **Interpretabilidad** | Alta | Baja | Media |
| **Costo Computacional** | Bajo | Alto | Medio |

---

## 7. Flujo de Trabajo de Predicción

### Proceso Completo de Predicción

El sistema genera predicciones a través de un **flujo de trabajo automatizado de 5 pasos**:

```
Paso 1: Recolección de Datos
         ↓
Paso 2: Predicción SARIMA
         ↓
Paso 3: Predicción LSTM
         ↓
Paso 4: Fusión Híbrida
         ↓
Paso 5: Clasificación de Alerta
```

### Desglose Paso a Paso

#### Paso 1: Recolección de Datos

```python
time_range = TimeRange.last_n_days(10)  # Últimos 10 días
sensor_data = fetch_from_TTS(time_range)
# Resultado: ~2,880 lecturas de sensores (288 por día × 10 días)
```

**Actividades:**
- Conectar a la API de The Things Stack
- Recuperar 10 días de datos de sensores
- Filtrar y validar lecturas
- Remuestrear a intervalos de 5 minutos
- Interpolar valores faltantes

**Salida:** Dataset limpio con temperatura, humedad, velocidad del viento

---

#### Paso 2: Predicción SARIMA

```python
# Preparación de Datos
temperature_series = extract_temperature(sensor_data)
resampled_series = resample_to_5min(temperature_series)

# Entrenamiento del Modelo (si no está en caché)
model = SARIMAX(resampled_series, order=(0,0,1), seasonal_order=(0,1,2,144))
fitted_model = model.fit()

# Pronóstico
forecast = fitted_model.forecast(steps=12)  # Próxima 1 hora
min_forecast_temp = min(forecast)

# Cálculo de Probabilidad
sarima_probability = calculate_frost_probability(min_forecast_temp)
```

**Salida:** Probabilidad SARIMA (ej., 0.62 = 62%)

---

#### Paso 3: Predicción LSTM

```python
# Preparación de Datos
df = prepare_multivariate_data(sensor_data)  # Temp, Humedad, Viento
scaled_data = MinMaxScaler().fit_transform(df)

# Creación de Secuencias
sequences = create_sequences(scaled_data, sequence_length=144)
# Resultado: tensor [batch_size, 144, 3]

# Entrenamiento del Modelo (si no está en caché)
model = build_lstm_model()
model.fit(sequences, targets, epochs=50, validation_split=0.2)

# Predicción
last_sequence = scaled_data[-144:]  # Últimas 12 horas
lstm_probability = model.predict(last_sequence)
```

**Salida:** Probabilidad LSTM (ej., 0.71 = 71%)

---

#### Paso 4: Fusión Híbrida

```python
# Promedio ponderado (LSTM 60%, SARIMA 40%)
hybrid_probability = (sarima_probability * 0.4) + (lstm_probability * 0.6)

# Ejemplo:
# SARIMA: 0.62 (62%)
# LSTM:   0.71 (71%)
# HYBRID: (0.62 × 0.4) + (0.71 × 0.6) = 0.674 (67.4%)
```

**Salida:** Probabilidad final de helada (ej., 0.674 = 67.4%)

---

#### Paso 5: Clasificación de Alerta

```python
def determine_frost_level(probability: float) -> FrostLevel:
    if probability > 0.70:
        return FrostLevel.FROST_EXPECTED     # Alto riesgo
    elif probability < 0.30:
        return FrostLevel.NO_FROST           # Bajo riesgo
    else:
        return FrostLevel.POSSIBLE_FROST     # Riesgo medio

# Ejemplo: 67.4% → POSSIBLE_FROST
```

**Salida:** Clasificación de nivel de helada + probabilidad

---

### Ejemplo Completo de Ejecución

```
🌡️ ======================================================== 🌡️
           INICIANDO PROCESO DE PREDICCIÓN DE HELADAS
🌡️ ======================================================== 🌡️

[PREDICTION] Paso 1: Obteniendo datos de sensores de los últimos 10 días...
[PREDICTION] ✓ Se recuperaron 2,847 lecturas de sensores

[PREDICTION] Paso 2: Ejecutando predicción del modelo SARIMA...
[SARIMA] Serie de temperatura preparada: 2,880 puntos de datos
[SARIMA] Construyendo modelo SARIMAX con order=(0,0,1) seasonal=(0,1,2,144)...
[SARIMA] ¡Ajuste del modelo completado exitosamente!
[PREDICTION] ✓ Probabilidad SARIMA: 62%

[PREDICTION] Paso 3: Ejecutando predicción del modelo LSTM...
[LSTM] Datos preparados: 2,880 puntos de datos
[LSTM] Se crearon 2,736 secuencias para entrenamiento
[LSTM] ¡Entrenamiento completado exitosamente!
[PREDICTION] ✓ Probabilidad LSTM: 71%

[PREDICTION] Paso 4: Calculando predicción híbrida...
[PREDICTION] Fórmula híbrida: (SARIMA * 0.4) + (LSTM * 0.6)
[PREDICTION] ✓ Probabilidad híbrida: 67.4%

============================================================
✓ PREDICCIÓN COMPLETADA
  Nivel de Helada: possible_frost
  Probabilidad: 67.4%
============================================================
```

---

## 8. Reglas de Decisión y Sistema de Alertas

### Clasificación de Nivel de Helada

El sistema usa **clasificación de riesgo de tres niveles**:

```python
if probability > 70%:
    ❄️ HELADA ESPERADA (Alto Riesgo)
elif probability < 30%:
    ✅ SIN HELADA ESPERADA (Bajo Riesgo)
else:
    ⚠️ POSIBLE HELADA (Riesgo Medio)
```

### Categorías de Riesgo

#### 1. HELADA ESPERADA (>70%)

**Significado:** Alta confianza de que ocurrirá helada

**Mensaje de WhatsApp:**
```
¡Hola! [Nombre del Agricultor]

🥶 *ALERTA DE HELADA* 🥶

¡Se esperan heladas esta noche!
Probabilidad: 75.5%

Por favor, tome medidas de protección para sus cultivos.
```

**Acciones Recomendadas:**
- Activar medidas de protección contra heladas inmediatamente
- Cubrir cultivos sensibles
- Desplegar máquinas de viento o calentadores si están disponibles
- Monitorear temperatura durante toda la noche

---

#### 2. POSIBLE HELADA (30-70%)

**Significado:** Condiciones inciertas, la helada puede ocurrir

**Mensaje de WhatsApp:**
```
¡Hola! [Nombre del Agricultor]

⚠️ *ADVERTENCIA DE HELADA* ⚠️

Posibles condiciones de helada esta noche.
Probabilidad: 55.0%

Monitoree las condiciones y esté preparado.
```

**Acciones Recomendadas:**
- Mantenerse alerta y monitorear condiciones
- Preparar equipo de protección
- Revisar actualizaciones del pronóstico
- Estar listo para actuar si las condiciones empeoran

---

#### 3. SIN HELADA ESPERADA (<30%)

**Significado:** Baja confianza de que ocurra helada

**Mensaje de WhatsApp:**
```
¡Hola! [Nombre del Agricultor]

✅ *SIN HELADA ESPERADA* ✅

No se esperan heladas esta noche.
Probabilidad: 15.0%

¡Las condiciones se ven favorables!
```

**Acciones Recomendadas:**
- Operaciones normales
- No se necesitan medidas especiales
- Monitoreo rutinario de cultivos

---

### Agregación de Alerta Diaria

#### ¿Por Qué Promedio Diario?

El sistema genera predicciones **3 veces por día** (3 AM, 12 PM, 4 PM), pero envía solo **una alerta** a las 5 PM usando la **probabilidad promedio diaria**.

**Razón:**
- Reduce la fatiga de alertas
- Proporciona evaluación consolidada de riesgo
- Captura cómo evoluciona el riesgo durante el día
- Más confiable que una sola instantánea

#### Método de Cálculo

```python
# Ejemplo: Tres predicciones hechas hoy
prediction_1 (3:00 AM):  62% probabilidad
prediction_2 (12:00 PM): 58% probabilidad
prediction_3 (4:00 PM):  71% probabilidad

# Promedio diario
daily_avg = (62% + 58% + 71%) / 3 = 63.7%

# Alerta enviada a las 5:00 PM
Clasificación: POSSIBLE_FROST (30-70%)
```

---

### Arquitectura del Sistema de Notificación

```
┌──────────────────────────────────────────────────────┐
│           Repositorio de Predicciones                 │
│   (Almacena todas las predicciones diarias con       │
│    marcas de tiempo)                                  │
└─────────────────────┬────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────┐
│      Calcular Probabilidad Promedio Diaria           │
│   (Promedio de todas las predicciones del día)       │
└─────────────────────┬────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────┐
│          Determinar Nivel de Helada                   │
│     (Aplicar reglas de clasificación >70%, <30%)     │
└─────────────────────┬────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────┐
│          Repositorio de Agricultores                  │
│  (Obtener agricultores registrados con números        │
│   de teléfono)                                        │
└─────────────────────┬────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────┐
│    Servicio de Notificación WhatsApp de Twilio       │
│ (Enviar alertas personalizadas a cada agricultor)    │
└──────────────────────────────────────────────────────┘
```

---

### Personalización

Cada agricultor recibe un **mensaje personalizado** con su nombre:

```python
# Sin registro
"¡Hola! [Saludo genérico]"

# Con registro
"¡Hola! Gabriela Guevara"
"¡Hola! María González"
```

**Estructura de Datos del Agricultor:**
```json
{
  "first_name": "Gabriela",
  "last_name": "Guevara",
  "phone_number": "+573012592676",
  "lot_address": "Finca La Esperanza, Vereda El Bosque",
  "registered_at": "2025-10-29T17:33:25.785674"
}
```

---

## 9. Automatización y Programación

### Programación Automatizada de Trabajos

El sistema funciona **completamente automatizado** con el siguiente horario:

```python
# Trabajos de Predicción (3 veces al día)
3:00 AM   → Predicción #1 (pronóstico de madrugada)
12:00 PM  → Predicción #2 (actualización del mediodía)
4:00 PM   → Predicción #3 (pronóstico de tarde)

# Trabajo de Alerta (una vez al día)
5:00 PM   → Enviar Alerta por WhatsApp (promedio diario)

# Trabajo de Actualización de Datos (continuo)
Cada 5 minutos → Actualizar datos de sensores desde TTS
```

### Tecnología de Programación

**APScheduler** (Advanced Python Scheduler) - Implementación AsyncIO

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = AsyncIOScheduler()

# Agregar trabajos de predicción
scheduler.add_job(run_prediction_job, CronTrigger(hour=3, minute=0))
scheduler.add_job(run_prediction_job, CronTrigger(hour=12, minute=0))
scheduler.add_job(run_prediction_job, CronTrigger(hour=16, minute=0))

# Agregar trabajo de alerta
scheduler.add_job(send_daily_alert_job, CronTrigger(hour=17, minute=0))

# Agregar trabajo de actualización de datos
scheduler.add_job(update_sensor_data, CronTrigger(minute="*/5"))

scheduler.start()
```

### Línea de Tiempo del Flujo de Trabajo Diario

```
00:00 ─────────────────────────────────────────────── 24:00
       │           │              │         │
     3:00        12:00          16:00     17:00
       │           │              │         │
   Predicción  Predicción    Predicción  Alerta
      #1          #2            #3       Enviada
       │           │              │         │
       └───────────┴──────────────┴─────────┘
              Se Calcula el Promedio Diario
```

### ¿Por Qué Este Horario?

**Predicción de las 3:00 AM:**
- Captura el enfriamiento nocturno
- Advertencia temprana antes del amanecer (momento más frío)

**Predicción de las 12:00 PM:**
- Actualización del mediodía con nuevos datos
- Ajusta el pronóstico basándose en condiciones matutinas

**Predicción de las 4:00 PM:**
- Predicción final antes del anochecer
- Más precisa con los datos del día completo

**Alerta de las 5:00 PM:**
- Enviada después de que todas las predicciones se completen
- Los agricultores tienen tiempo para prepararse antes de la tarde
- El promedio diario proporciona evaluación consolidada de riesgo

---

### Estrategia de Caché de Modelos

Para optimizar el rendimiento, **los modelos entrenados se almacenan en caché** en memoria:

```python
# Primera predicción del día
[SARIMA] Construyendo modelo... (20-40 segundos)
[LSTM] Entrenando modelo... (2-3 minutos)

# Predicciones subsecuentes
[SARIMA] ⚡ Usando modelo en caché (instantáneo)
[LSTM] ⚡ Usando modelo en caché (instantáneo)
```

**Beneficios:**
- Predicciones más rápidas (segundos vs minutos)
- Uso reducido de CPU
- Modelo consistente a través de predicciones diarias

**Validez del Caché:**
- Modelos almacenados en caché hasta el reinicio del servidor
- Actualizados cuando se detectan cambios significativos en los datos

---

## 10. Stack Técnico

### Framework Backend

**FastAPI** (Python)
- Framework web moderno y rápido
- Documentación automática de API (Swagger/OpenAPI)
- Type hints y validación con Pydantic
- Soporte async para operaciones concurrentes

### Bibliotecas de Aprendizaje Automático

**SARIMA:**
- `statsmodels` 0.14.0 - Modelado estadístico de series temporales
- `pandas` 2.1.4 - Manipulación de datos
- `numpy` 1.24.3 - Computación numérica

**LSTM:**
- `tensorflow` 2.13.0 - Framework de aprendizaje profundo
- `keras` (incluido en TensorFlow) - API de alto nivel para redes neuronales
- `scikit-learn` 1.3.2 - Preprocesamiento y escalado de datos

### Servicios Externos

**Integración IoT:**
- **The Things Stack (TTS)** - Servidor de red LoRaWAN
- `httpx` 0.25.2 - Cliente HTTP asíncrono para llamadas a API

**Notificaciones:**
- **API de WhatsApp de Twilio** - Entrega de mensajes
- `twilio` 8.10.0 - SDK oficial de Python

### Programación y Async

- `apscheduler` 3.10.4 - Programación de trabajos
- `asyncio` (incorporado en Python) - Programación asíncrona

### Configuración

- `python-dotenv` 1.0.0 - Gestión de variables de entorno
- `pydantic-settings` 2.1.0 - Validación de configuración

### API y Validación

- `pydantic` 2.5.0 - Validación y serialización de datos
- `uvicorn` 0.24.0 - Servidor ASGI para FastAPI

---

### Requisitos del Sistema

**Versión de Python:** 3.9+

**Memoria:**
- Mínimo: 2 GB RAM
- Recomendado: 4 GB RAM (para TensorFlow)

**Almacenamiento:**
- Aplicación: ~500 MB
- Modelos: ~100 MB
- Datos: ~50 MB (10 días de datos de sensores)

**Red:**
- Conexión estable a internet para APIs de TTS y Twilio
- Acceso HTTPS saliente (443) requerido

---

### Arquitectura de Despliegue

```
┌─────────────────────────────────────────────────────┐
│              Sensores LoRaWAN                        │
│      (Temperatura, Humedad, Velocidad del Viento)    │
└───────────────────────┬─────────────────────────────┘
                        │ Protocolo LoRaWAN
                        ▼
┌─────────────────────────────────────────────────────┐
│            The Things Stack (TTS)                    │
│      (Servidor de Red IoT y Almacenamiento)         │
└───────────────────────┬─────────────────────────────┘
                        │ API HTTPS
                        ▼
┌─────────────────────────────────────────────────────┐
│          Backend FastAPI (Este Sistema)              │
│  ┌──────────────────────────────────────────────┐  │
│  │ Recolección de Datos → Modelos ML → Predict. │  │
│  │   (Programador ejecuta trabajos 24/7)        │  │
│  └──────────────────────────────────────────────┘  │
└───────────────────────┬─────────────────────────────┘
                        │ API HTTPS
                        ▼
┌─────────────────────────────────────────────────────┐
│              API de WhatsApp de Twilio               │
└───────────────────────┬─────────────────────────────┘
                        │ Mensajes de WhatsApp
                        ▼
┌─────────────────────────────────────────────────────┐
│                   Agricultores                       │
│           (Reciben alertas en sus teléfonos)        │
└─────────────────────────────────────────────────────┘
```

---

## 11. Implementación en el Mundo Real

### Despliegue Actual

**Ubicación:** Área agrícola rural (Colombia)
**Cobertura:** Múltiples lotes de fincas
**Usuarios Activos:** 2 agricultores registrados (escalable a cientos)

### Agricultores Registrados

```json
[
  {
    "nombre": "Gabriela Guevara",
    "teléfono": "+573012592676",
    "finca": "Finca La Esperanza, Vereda El Bosque",
    "registrado": "29 de octubre de 2025"
  },
  {
    "nombre": "María González",
    "teléfono": "+573001234567",
    "finca": "Finca El Paraíso, Lote 24",
    "registrado": "29 de octubre de 2025"
  }
]
```

### Red de Sensores

**Tipo de Dispositivo:** Sensores ambientales LoRaWAN
**Intervalo de Transmisión:** Cada 5 minutos
**Red:** Gateway LoRaWAN The Things Stack (TTS)
**Área de Cobertura:** Múltiples lotes de fincas dentro del rango LoRaWAN

**Parámetros Medidos:**
- Temperatura: °C (Celsius)
- Humedad: % (Humedad relativa)
- Velocidad del Viento: m/s (Metros por segundo)

---

### Endpoints de API

El sistema expone varios endpoints REST API:

#### 1. Endpoint de Webhook
```
POST /api/v1/webhook
```
Recibe datos de sensores en tiempo real desde The Things Stack.

**Caso de Uso:** TTS envía mensajes uplink cuando los sensores transmiten datos

---

#### 2. Predicción Manual
```
POST /api/v1/predict
```
Activar manualmente una predicción de heladas (fuera de horarios programados).

**Caso de Uso:** Predicción bajo demanda para pruebas o evaluación de riesgo inmediata

**Ejemplo de Respuesta:**
```json
{
  "probability": 0.674,
  "frost_level": "possible_frost",
  "model_type": "hybrid",
  "sarima_probability": 0.62,
  "lstm_probability": 0.71,
  "created_at": "2025-10-31T16:00:00Z"
}
```

---

#### 3. Enviar Alerta
```
POST /api/v1/send-alert
```
Enviar manualmente alerta por WhatsApp con la última predicción.

**Caso de Uso:** Probar notificaciones o enviar alertas de emergencia

---

#### 4. Registro de Agricultores
```
POST /api/v1/farmers/register
```
Registrar nuevos agricultores para recibir alertas.

**Cuerpo de la Solicitud:**
```json
{
  "first_name": "Juan",
  "last_name": "Pérez",
  "phone_number": "+573001234567",
  "lot_address": "Finca Los Andes, Vereda Norte"
}
```

---

#### 5. Obtener Todos los Agricultores
```
GET /api/v1/farmers
```
Listar todos los agricultores registrados.

**Respuesta:**
```json
{
  "farmers": [
    {
      "first_name": "Gabriela",
      "last_name": "Guevara",
      "phone_number": "+573012592676",
      "lot_address": "Finca La Esperanza",
      "registered_at": "2025-10-29T17:33:25Z"
    }
  ],
  "total": 1
}
```

---

#### 6. Verificación de Salud
```
GET /health
```
Verificar si la API está funcionando.

**Respuesta:**
```json
{
  "status": "healthy",
  "service": "frost-prediction-api"
}
```

---

### Experiencia del Usuario

**Para Agricultores (Usuarios No Técnicos):**

1. **Registro:** Registro único con número de teléfono
2. **Cero Interacción:** No hay app para instalar, no se requiere inicio de sesión
3. **Alertas por WhatsApp:** Reciben mensajes en plataforma familiar
4. **Orientación Clara:** Niveles de riesgo simples con elementos de acción
5. **Personalizado:** Mensajes dirigidos a ellos por nombre
6. **Idioma Español:** Accesible en idioma local

**Ejemplo de un Día en la Vida:**

```
5:00 PM - El teléfono del agricultor vibra
Mensaje de WhatsApp recibido:

"¡Hola! Gabriela Guevara

⚠️ *ADVERTENCIA DE HELADA* ⚠️

Posibles condiciones de helada esta noche.
Probabilidad: 63.7%

Monitoree las condiciones y esté preparado."

Acción: Gabriela prepara equipo de protección contra heladas
```

---

## 12. Resultados e Impacto

### Rendimiento del Sistema

**Precisión de Predicción:**
- El modelo híbrido combina fortalezas de ambos enfoques
- SARIMA captura patrones temporales
- LSTM captura relaciones multivariables
- El promedio diario reduce falsos positivos

**Métricas Operacionales:**
- **Predicciones por día:** 3 (3 AM, 12 PM, 4 PM)
- **Alertas por día:** 1 (5 PM con promedio diario)
- **Tiempo de entrenamiento del modelo:**
  - SARIMA: 20-40 segundos
  - LSTM: 2-3 minutos
  - Predicciones en caché: <1 segundo
- **Tiempo de entrega de alertas:** <5 segundos vía Twilio
- **Tiempo de actividad del sistema:** Operación automatizada 24/7

---

### Beneficios para los Agricultores

**Impacto Económico:**
1. **Prevención de Pérdida de Cultivos**
   - La advertencia temprana permite medidas de protección
   - Reduce el daño por heladas a cultivos sensibles
   - Protege el sustento e ingresos del agricultor

2. **Eficiencia de Costos**
   - Servicio de alerta gratuito (sin tarifas de suscripción)
   - No se requiere compra de hardware (usa sensores existentes)
   - Opera vía WhatsApp (no se necesita app especial)

3. **Ahorro de Tiempo**
   - Las alertas automatizadas eliminan el monitoreo manual del clima
   - Pronóstico diario consolidado (no actualizaciones constantes)
   - La orientación clara de acción reduce el tiempo de decisión

**Gestión de Riesgo:**
- **Alertas de alta confianza (>70%):** Tomar acción protectora inmediata
- **Alertas de confianza media (30-70%):** Mantenerse preparado
- **Alertas de baja confianza (<30%):** Operaciones normales

---

### Escalabilidad

**Estado Actual:** 2 agricultores, 1 red de sensores
**Escala Potencial:** Cientos de agricultores, múltiples regiones

**Estrategia de Escalado:**
1. **Escala de Usuarios:**
   - Agregar agricultores vía endpoint de registro API
   - Incremento mínimo de costo (solo mensajes de WhatsApp de Twilio)
   - Alertas personalizadas para cada agricultor

2. **Escala Geográfica:**
   - Desplegar redes adicionales de sensores LoRaWAN
   - Múltiples integraciones de aplicaciones TTS
   - Modelos de predicción específicos de región

3. **Escala de Características:**
   - Agregar umbrales específicos por cultivo
   - Soporte multiidioma (actualmente español)
   - Dashboard de analítica histórica
   - Integración con otros servicios meteorológicos

---

### Impacto Ambiental y Social

**Resiliencia Climática:**
- Ayuda a los agricultores a adaptarse a patrones climáticos impredecibles
- Apoya prácticas agrícolas sostenibles
- Reduce la necesidad de calentamiento protector excesivo (conservación de energía)

**Transferencia de Conocimiento:**
- Demuestra aplicación práctica de IA en agricultura
- Tecnología accesible para comunidades rurales
- Valor educativo para ingeniería agrícola

**Seguridad Alimentaria:**
- Protege rendimientos de cultivos del daño por heladas
- Apoya la producción local de alimentos
- Contribuye a la estabilidad agrícola

---

## 13. Mejoras Futuras

### Mejoras a Corto Plazo (3-6 meses)

#### 1. Modelos de Predicción Mejorados
- **Métodos de Ensamble:** Agregar modelos Random Forest, XGBoost
- **Ponderación Dinámica:** Ajustar pesos SARIMA/LSTM según condiciones
- **Pronóstico Más Largo:** Extender de 1 hora a 6 horas de predicción
- **Intervalos de Confianza:** Proporcionar rangos de incertidumbre de predicción

#### 2. Fuentes de Datos Adicionales
- **APIs del Clima:** Integrar pronósticos meteorológicos externos (OpenWeatherMap)
- **Sensores de Suelo:** Agregar datos de temperatura y humedad del suelo
- **Datos Satelitales:** Incorporar datos de cobertura de nubes y radiación
- **Múltiples Sensores:** Soportar múltiples ubicaciones de sensores por finca

#### 3. Interfaz de Usuario
- **Dashboard Web:** Visualización de predicciones en tiempo real
- **Analítica Histórica:** Ver predicciones pasadas y precisión
- **Portal del Agricultor:** Registro autoservicio y preferencias
- **Respaldo SMS:** Para usuarios sin WhatsApp

---

### Mejoras a Medio Plazo (6-12 meses)

#### 4. Modelos Específicos por Cultivo
- **Perfiles de Cultivos:** Diferentes umbrales para diferentes cultivos
  - Café: Crítico a <2°C
  - Fresas: Crítico a <-1°C
  - Flores: Crítico a <0°C
- **Etapa Fenológica:** Considerar etapa de crecimiento del cultivo en evaluación de riesgo
- **Personalización de Finca:** Modelos personalizados por microclima de finca

#### 5. Notificaciones Avanzadas
- **Multicanal:** SMS, Email, Notificaciones Push, Llamadas de Voz
- **Niveles de Severidad:** Diferenciar entre vigilancia y advertencia
- **Recomendaciones de Acción:** Medidas de protección específicas por cultivo
- **Alertas de Seguimiento:** Actualizaciones si el riesgo cambia significativamente

#### 6. Monitoreo y Reentrenamiento de Modelos
- **Seguimiento de Predicción:** Registrar eventos reales vs predichos de heladas
- **Métricas de Precisión:** Calcular y mostrar rendimiento del modelo
- **Reentrenamiento Automatizado:** Reentrenar modelos con nuevos datos mensualmente
- **Pruebas A/B:** Comparar versiones de modelos en producción

---

### Visión a Largo Plazo (1-2 años)

#### 7. Expansión Regional
- **Soporte Multi-Región:** Desplegar en múltiples países
- **Localización de Idioma:** Español, Inglés, Portugués, Francés
- **Modelos Regionales:** Entrenar modelos específicos para cada zona climática
- **Redes de Agricultores:** Compartir mejores prácticas comunitarias

#### 8. Capacidades Avanzadas de IA
- **IA Explicable:** Visualizar por qué el modelo hizo predicción específica
- **Aprendizaje por Transferencia:** Aplicar conocimiento de una región a otra
- **Mecanismos de Atención:** Identificar qué características influyen más en las predicciones
- **IA Generativa:** Explicaciones en lenguaje natural en alertas

#### 9. Ecosistema de Integración
- **Servicios Meteorológicos Gubernamentales:** Integración de pronósticos oficiales
- **Seguros Agrícolas:** Soporte de reclamaciones automatizado con registros de predicción
- **Sistemas de Gestión de Fincas:** Integración con plataformas agtech existentes
- **Instituciones de Investigación:** Compartir datos para estudios agrícolas

#### 10. Aplicación Móvil
- **Apps Nativas:** Aplicaciones iOS y Android
- **Modo Offline:** Ver predicciones almacenadas en caché sin internet
- **Notificaciones Push:** Alertas instantáneas sin costos de SMS/WhatsApp
- **Características Comunitarias:** Comunicación agricultor a agricultor

---

### Oportunidades de Investigación

**Colaboración Académica:**
- Publicar resultados en revistas de ingeniería agrícola
- Colaborar con universidades en mejoras de modelos
- Código abierto de componentes para la comunidad de investigación

**Investigación en Aprendizaje Automático:**
- Técnicas novedosas de fusión híbrida
- Aprendizaje por transferencia entre diferentes regiones agrícolas
- Métodos de explicabilidad para IA agrícola

**Investigación Agrícola:**
- Correlación entre predicciones y daño real de cultivos
- Tiempo óptimo de medidas de protección basado en predicciones
- Análisis de costo-beneficio de protección contra heladas guiada por IA

---

## 14. Conclusión

### Logros Clave

Este sistema de predicción de heladas impulsado por IA demuestra:

1. **Aplicación Práctica de IA**
   - Despliegue en el mundo real en entorno agrícola
   - Resuelve problema tangible para agricultores
   - Tecnología accesible para comunidades rurales

2. **Excelencia Técnica**
   - Arquitectura Limpia para mantenibilidad
   - Enfoque ML híbrido combinando SARIMA y LSTM
   - Operación automatizada 24/7 con programación

3. **Diseño Centrado en el Usuario**
   - Alertas por WhatsApp (plataforma familiar)
   - Idioma español (idioma local)
   - Niveles de riesgo claros con orientación de acción
   - Mensajes personalizados

4. **Escalabilidad y Extensibilidad**
   - Arquitectura modular soporta expansión
   - Fácil agregar más agricultores o regiones
   - Fundamento para mejoras futuras

---

### Resumen de Impacto

**Para los Agricultores:**
- Las advertencias tempranas de heladas permiten acciones de protección
- Reduce el daño a cultivos y pérdidas económicas
- Servicio gratuito y accesible vía WhatsApp
- No se requiere experiencia técnica

**Para la Agricultura:**
- Apoya prácticas agrícolas resilientes al clima
- Protege la seguridad alimentaria y rendimientos de cultivos
- Demuestra valor de IoT + IA en agricultura
- Escalable a comunidades agrícolas más grandes

**Para la Tecnología:**
- Demostración práctica de ML en producción
- Enfoque de modelo híbrido muestra beneficio de métodos de ensamble
- Principios de Arquitectura Limpia en aplicación del mundo real
- Abierto para investigación y colaboración académica

---

### Puntos Clave para la Presentación

**Para Congreso Internacional:**

1. **Marco del Problema:**
   "Las heladas causan millones en pérdidas agrícolas anualmente. Los agricultores necesitan advertencias precisas y oportunas para proteger sus medios de vida."

2. **Innovación Técnica:**
   "Nuestro sistema ML híbrido combina análisis clásico de series temporales (SARIMA) con aprendizaje profundo (LSTM) para predicciones robustas."

3. **Impacto en el Mundo Real:**
   "Actualmente sirviendo a agricultores en Colombia con alertas automatizadas por WhatsApp. Cero barreras técnicas para adopción."

4. **Escalabilidad:**
   "Arquitectura diseñada para expansión a cientos de agricultores y múltiples regiones. El diseño modular soporta mejoras futuras."

5. **Accesibilidad:**
   "Usa plataforma familiar de WhatsApp, idioma español y niveles de riesgo claros. Tecnología que sirve, no intimida."

6. **Valor de Investigación:**
   "Abierto a colaboración con investigadores de ingeniería agrícola e IA. Oportunidades para mejoras de modelos y estudios de campo."

---

### Llamado a la Acción

**Para Investigadores:**
- Colaborar en mejoras de modelos
- Acceder a datos anonimizados para estudios
- Contribuir a componentes de código abierto

**Para Agricultores:**
- Registrarse para recibir alertas gratuitas
- Proporcionar retroalimentación sobre precisión de predicción
- Compartir con agricultores vecinos

**Para Inversionistas/ONGs:**
- Apoyar expansión a más regiones
- Financiar despliegues adicionales de sensores
- Asociarse para programas de resiliencia agrícola

**Para Ingenieros:**
- Contribuir al código base
- Proponer mejoras arquitectónicas
- Desarrollar características adicionales

---

### Contacto y Recursos

**Repositorio del Proyecto:** (Agregar URL de GitHub si es código abierto)

**Documentación Técnica:** README.md

**Documentación API:** http://[tu-dominio]/docs (Swagger UI)

**Arquitectura del Sistema:** Arquitectura Limpia con capas de cebolla

**Tecnologías:**
- Backend: FastAPI (Python)
- ML: TensorFlow (LSTM), Statsmodels (SARIMA)
- IoT: The Things Stack (LoRaWAN)
- Notificaciones: API de WhatsApp de Twilio
- Programación: APScheduler

---

## Apéndice: Glosario Técnico

**SARIMA:** Seasonal AutoRegressive Integrated Moving Average - Modelo clásico de pronóstico de series temporales

**LSTM:** Long Short-Term Memory - Tipo de red neuronal recurrente para datos secuenciales

**LoRaWAN:** Long Range Wide Area Network - Protocolo inalámbrico de bajo consumo para dispositivos IoT

**The Things Stack (TTS):** Servidor de red LoRaWAN para gestionar dispositivos sensores IoT

**IoT:** Internet of Things (Internet de las Cosas) - Red de dispositivos físicos con sensores y conectividad

**API:** Application Programming Interface - Interfaz de software para comunicación entre sistemas

**FastAPI:** Framework web moderno de Python para construir APIs

**TensorFlow/Keras:** Frameworks de código abierto de aprendizaje automático

**Arquitectura Limpia:** Patrón de diseño de software con estructura en capas e inversión de dependencias

**Modelo Híbrido:** Enfoque ML combinando múltiples modelos para mejorar precisión

**Probabilidad de Helada:** Probabilidad (0-100%) de que ocurran condiciones de helada

**Nivel de Helada:** Clasificación de riesgo (Sin Helada, Posible Helada, Helada Esperada)

---

**FIN DE LA GUÍA PARA CONGRESO**

---

*Este documento sirve como referencia completa para presentar el sistema de predicción de heladas impulsado por IA en congresos internacionales, conferencias académicas o foros técnicos. Cubre todos los aspectos desde el planteamiento del problema hasta la implementación técnica y el impacto en el mundo real.*

*Versión: 1.0*
*Última Actualización: 31 de octubre de 2025*
*Preparado para: Presentación en Congreso Internacional*
