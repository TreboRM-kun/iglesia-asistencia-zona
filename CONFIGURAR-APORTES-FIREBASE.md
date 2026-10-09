# Acceso seguro, aportes y datos por zona

Firebase Authentication con correo y contraseña está habilitado en este proyecto. La aplicación actualizada usa esa autenticación para iniciar sesión en **toda la aplicación**, incluidos los aportes. Ya no consulta ni guarda contraseñas en la ruta antigua `Usuarios`.

La versión que separa los datos por zona está publicada en GitHub Pages y las reglas de Realtime Database para los datos existentes ya están activas. Las nuevas reglas para comprobantes deben publicarse junto con la versión que las usa. Los comprobantes se comprimen y se guardan en una ruta protegida de Realtime Database; no requieren un bucket de Cloud Storage ni el plan Blaze.

## Estado del despliegue

La cuenta de Zona1 existe en Authentication y su perfil está asignado a `rol: "Facilitador"` y `salon: "Zona 1"`. La corrección ya está publicada; queda pendiente que el facilitador confirme que puede iniciar sesión.

## Cuentas

1. Las cuentas se administran en **Authentication > Users**. La aplicación convierte cada nombre de usuario al correo interno con dominio `@asistencia-iglesia-zonas.firebaseapp.com`.

## Aislamiento por zona publicado

La aplicación usa estas rutas separadas:

- `LideresPorZona/{salon}`
- `AsistenciasPorZona/{salon}`
- `FacilitadoresPorZona/{salon}`
- `DiscipuladoVirtualPorZona/{salonOrigen}`

Cada facilitador puede leer y actualizar únicamente el hijo correspondiente a su `salon`; administradores y supervisores pueden revisar todas las zonas. Los registros virtuales sin zona de origen y los registros del Pastor quedan disponibles solo para los revisores. La aplicación también borra su caché local al cambiar de usuario para que un navegador compartido no muestre datos de otra zona.

Los datos se migraron a las cuatro rutas nuevas y se conservó la exportación original como respaldo privado. La migración validada conservó los 174 líderes, 361 asistencias, 8 facilitadores y 8 registros de discipulado virtual. Las asistencias virtuales se repartieron según su zona de origen cuando existe; las que no tienen zona quedaron bajo `Virtual`. El script `migrar-datos-por-zona.py` queda disponible para futuras migraciones.

## Cumpleaños visibles para todas las zonas

El calendario y la cinta semanal leen `CumpleanosPorZona`, un índice con solo nombre y fecha de cumpleaños, separado por zona. Los usuarios autenticados pueden consultarlo, pero no obtienen acceso a los demás datos privados de líderes de otras zonas. Administradores completan el índice al iniciar sesión; los cambios posteriores a líderes y cumpleaños actualizan la zona correspondiente.

Al publicar una versión que use este índice, publique también `database.rules.json`. Después, inicie sesión una vez como administrador para completar los cumpleaños que ya existían. Si las reglas todavía no están activas, la aplicación avisará que no pudo cargar los cumpleaños compartidos.

Si se vuelve a ejecutar una migración, guarde tanto la exportación como el resultado en una ubicación privada:

```powershell
python .\migrar-datos-por-zona.py `
  --source "RUTA\A\EXPORTACION-COMPLETA.json" `
  --output "RUTA\PRIVADA\migracion-por-zona.json"
```

El archivo de migración contiene información personal y debe mantenerse privado. No lo suba al repositorio ni importe el archivo completo en la raíz de la base: eso podría reemplazar otros datos.

## Alcance de las reglas preparadas

- Sin una cuenta autenticada y un perfil válido en `/Perfiles`, las rutas de datos de la aplicación quedan denegadas. La antigua ruta `Usuarios`, que contenía contraseñas, no se concede a la aplicación.
- Los perfiles no pueden modificarse desde la aplicación; su mantenimiento requiere una operación administrativa.
- Los datos históricos de las rutas antiguas se conservaron, pero las reglas no conceden acceso a las antiguas rutas compartidas de líderes y asistencias. La lista separada de líderes del Pastor permanece accesible solo para administradores y supervisores; los facilitadores no intentan leerla.
- Los aportes tienen restricciones de servidor: facilitadores pueden registrar, editar y eliminar únicamente aportes propios de su zona; administradores pueden registrar aportes en cualquier zona y consultar todas las semanas; supervisores conservan acceso de consulta. Nadie puede editar ni eliminar una transacción una vez alcanzado el cierre del sábado.
- Cada aporte conserva `fechaCierre` como el inicio del domingo siguiente (hora de Venezuela). Las reglas de Realtime Database impiden registrar semanas ya cerradas y bloquean ediciones o eliminaciones una vez superado ese instante. Los aportes cerrados continúan visibles para Administración al elegir su semana y dejan de aparecer en la lista de la zona.
- Las referencias se reservan en `ReferenciasAportesLimpieza/{referencia}` dentro de la misma operación atómica que registra el aporte, para rechazar referencias repetidas incluso entre zonas. Cada índice conserva la referencia, el ID, la zona y el cierre; el UID se incluye cuando el registro histórico lo tiene. Las reglas enumeran explícitamente y validan cada campo permitido del índice; sin validadores para ID, zona, referencia y cierre, `$other` rechaza la escritura incluso cuando el administrador tiene permiso. Un facilitador solo puede leer el índice de sus propios aportes. La primera vez que un administrador abre la consulta, la aplicación completa cierres, reservas históricas e índices `AportesLimpiezaPorUsuario/{uid}/{id}` para que cada facilitador pueda ver y corregir sus aportes aún abiertos. La regla del campo `fechaCierre` permite al administrador agregar un cierre faltante o acortar uno todavía vigente durante esta preparación, sin permitir que se extienda ni alterar un registro ya cerrado. La validación de migración preserva íntegramente los campos de aportes históricos incompletos (por ejemplo, registros anteriores sin UID o zona) mientras completa únicamente el cierre. Los cierres históricos ya vencidos se conservan sin cambios.
- El módulo de aportes guarda los comprobantes comprimidos en `ComprobantesAportes/{uid}/{id}` dentro de Realtime Database. Facilitadores pueden ver sus propios comprobantes; administradores y supervisores pueden revisar todos. Las imágenes se descargan únicamente al pulsar el botón para ver el comprobante.
- La bitácora y los respaldos conservan permisos de revisión. Los respaldos automáticos de cambios realizados por facilitadores ya no se generan; los cambios siguen registrándose en la bitácora.

`database.rules.json` contiene las reglas de Realtime Database para proteger las transacciones, los índices de referencias y usuario, y sus comprobantes. Publique estas reglas en Firebase antes de publicar la interfaz que depende de ellas. Después, inicie sesión como administrador y abra el control de aportes para completar los índices históricos. `firebase.json` vincula los archivos de reglas para Firebase CLI; el sitio se aloja en GitHub Pages. El proyecto puede seguir en Spark para usar los comprobantes guardados en Realtime Database; Cloud Storage no forma parte de este flujo.
