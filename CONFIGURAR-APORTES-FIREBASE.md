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

El calendario y la cinta semanal leen el índice `CumpleanosPorZona`, que solo contiene nombres y fechas de cumpleaños separados por zona. Los usuarios autenticados con un perfil de la aplicación pueden consultarlo sin obtener acceso a los demás datos privados de otras zonas. Al iniciar sesión, un administrador completa el índice con los cumpleaños existentes; los cambios posteriores en líderes y cumpleaños actualizan las zonas correspondientes.

Publique las reglas de `database.rules.json` en Firebase y luego inicie sesión una vez como administrador para cargar los cumpleaños existentes. Si Firebase no permite leer o actualizar el índice, la aplicación avisa en pantalla.

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
- Los aportes sí tienen restricciones de servidor: los facilitadores solo pueden crear aportes para su zona y leer los propios; administradores y supervisores pueden revisar todos y cambiar su estado.
- El módulo de aportes guarda los comprobantes comprimidos en `ComprobantesAportes/{uid}/{id}` dentro de Realtime Database. Solo los facilitadores pueden crear o limpiar comprobantes temporales de su propia cuenta; solo administradores y supervisores pueden leerlos. Las imágenes se descargan únicamente al pulsar el botón para ver el comprobante.
- La bitácora y los respaldos conservan permisos de revisión. Los respaldos automáticos de cambios realizados por facilitadores ya no se generan; los cambios siguen registrándose en la bitácora.

`database.rules.json` contiene las reglas de Realtime Database para proteger las transacciones y sus comprobantes; después de publicar los cambios, estas reglas deben quedar activas en Firebase. `firebase.json` vincula los archivos de reglas para Firebase CLI; el sitio se aloja en GitHub Pages. El proyecto puede seguir en Spark para usar los comprobantes guardados en Realtime Database; Cloud Storage no forma parte de este flujo.
