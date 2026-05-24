# Sistema de Rendición de Gastos e Infracciones Financieras 📊

Este sistema modular automatiza el ingreso, auditoría técnica, visación jerárquica y dispersión bancaria de las rendiciones de gastos corporativos, aplicando dinámicamente las reglas de negocio e infracciones del sistema.

---

## 🚀 Instrucciones de Ejecución

Para iniciar la interfaz gráfica del sistema, sigue estrictamente estos pasos:

1. Abre el explorador de archivos de tu sistema operativo y navega hasta la carpeta del proyecto.
2. Localiza el archivo **`app.py`**.
3. Haz **clic derecho** sobre `app.py` y selecciona la opción **Abrir en la Terminal** (o *Open in Terminal*).
4. En la ventana de la terminal que se acaba de abrir, escribe y ejecuta el siguiente comando:

```bash
py -m streamlit run app.py

```

5. El sistema se compilará y abrirá automáticamente una pestaña en tu navegador web predeterminado (usualmente en la dirección `http://localhost:8501`).

---

## 🔑 Credenciales de Acceso (Entorno de Pruebas)

Utiliza los siguientes usuarios para simular los distintos roles del flujo de trabajo. Para este entorno temporal, **todos los usuarios comparten la misma contraseña**.

| Usuario | Contraseña | Rol Asignado |
| --- | --- | --- |
| **francisco** | `123` | Colaborador / Rendidor |
| **catalina** | `123` | Analista de Finanzas / Auditor Técnico |
| **gerencia** | `123` | Gerente de Finanzas (Aprobador Jerárquico) |
| **tesorero** | `123` | Tesorero Liquidador |

---

## 👤 Roles y Capacidades del Sistema

Una vez que hayas iniciado sesión con un usuario, la interfaz adaptará sus módulos según sus atribuciones:

### 1. Rol Rendidor (Francisco)

* **Ingreso de Comprobantes:** Permite registrar documentos en tiempo real formateando automáticamente el **RUT** e incluyendo puntos de miles al **Monto CLP**.
* **Persistencia Integrada:** Permite guardar documentos como **Borrador** para continuar la edición más tarde, o **Enviar al Flujo** de aprobación.
* **Alertas de Negocio:** Si envía un documento emitido hace más de 30 días, el sistema lo detectará automáticamente como *Caducidad Fiscal* y lo congelará como Borrador para revisión.
* **Trazabilidad:** Posee una sección de **Mis Rendiciones Recientes** donde puede ver el estado actual de sus folios y un historial detallado (*Logs*) de quién y cuándo modificó su documento. Además, si el Analista le *Observa* un gasto, se habilita un botón dinámico para corregirlo inmediatamente.

### 2. Rol Analista de Finanzas (Catalina)

* **Bandeja de Auditoría:** Visualiza y evalúa técnicamente todos los folios en estado `Pendiente` (que no posean bloqueos jerárquicos).
* **Simulación OCR:** Permite expandir la evidencia digital para contrastar los metadatos extraídos por el sistema (RUT, Folio, Monto) bajo verificación de integridad Hash SHA-256.
* **Flujo de Decisiones:** * **Aprobar:** Modifica el estado a `Autorizado` derivando el caso a Tesorería.
* **Observar (Excepción E1):** Si el documento posee reparos, exige un comentario obligatorio y devuelve el folio al Rendidor en estado `Observado` para su posterior corrección.



### 3. Rol Gerente de Finanzas (Gerencia)

* **Bandeja de Control Excepcional:** Módulo crítico para la visación de rendiciones que violan umbrales del sistema.
* **Detección Dinámica de Infracciones:**
* **Alta Cuantía (BR-05):** Filtra automáticamente gastos mayores a **$500,000 CLP**.
* **Crítico:** Detecta si un documento además de ser de alto monto posee la fecha de emisión vencida.


* **Visación:** Al otorgar el *Flag de Visación*, remueve el bloqueo jerárquico del documento para que el Analista pueda proceder con la auditoría técnica regular.
* **Rechazo Definitivo:** Cancela la solicitud por completo, asignándole el estado final de `Rechazado`.

### 4. Rol Tesorero Liquidador (Tesorero)

* **Bandeja de Cierre:** Administra la fase final de dispersión bancaria para los documentos que ya cuentan con el estado `Autorizado`.
* **Egreso Bancario:** Registra el pago exitoso del reembolso, actualizando el estado de la rendición a `Pagado` y generando el log de auditoría correspondiente.
* **Retención por Liquidez (Excepción E6):** En caso de que la organización experimente quiebres de caja temporales o falta de liquidez inmediata, permite encolar el documento bajo el estado `Autorizado - Pendiente de Fondos` para resguardar la estabilidad financiera hasta nuevo aviso.
