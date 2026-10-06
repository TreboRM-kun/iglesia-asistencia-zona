# Acceso seguro, aportes y datos por zona

Firebase Authentication con correo y contraseña está habilitado en este proyecto. La aplicación actualizada usa esa autenticación para iniciar sesión en **toda la aplicación**, incluidos los aportes. Ya no consulta ni guarda contraseñas en la ruta antigua `Usuarios`.

La versión que separa los datos por zona está publicada en GitHub Pages y las reglas definitivas de Realtime Database ya están activas. Se comprobó que las lecturas anónimas de la raíz, de las rutas nuevas, de la ruta antigua de líderes y de los aportes devuelven HTTP 401. El proyecto sigue en Spark y todavía no tiene un bucket para guardar comprobantes.

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
- Los datos históricos de las rutas antiguas se conservaron, pero las reglas definitivas ya no conceden acceso a ellas. La aplicación publicada usa las rutas separadas por zona.
- Los aportes sí tienen restricciones de servidor: los facilitadores solo pueden crear aportes para su zona y leer los propios; administradores y supervisores pueden revisar todos y cambiar su estado.
- El módulo de aportes está disponible. La carga y visualización de comprobantes requiere crear el bucket de Storage y publicar sus reglas; aún no está disponible porque no hay una cuenta de Cloud Billing asociada al proyecto.
- La bitácora y los respaldos conservan permisos de revisión. Los respaldos automáticos de cambios realizados por facilitadores ya no se generan; los cambios siguen registrándose en la bitácora.

`database.rules.json` contiene las reglas definitivas que ya están publicadas. `firebase.json` vincula los archivos de reglas para Firebase CLI; el sitio se aloja en GitHub Pages. El propietario autorizó Blaze, pero Firebase Console indica que no existe una cuenta de Cloud Billing disponible para asociar. El propietario debe crear o vincular esa cuenta antes de habilitar Storage, crear el bucket y desplegar `storage.rules`.
