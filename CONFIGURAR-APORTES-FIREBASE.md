# Migración segura de accesos y aportes

Firebase Authentication con correo y contraseña está habilitado en este proyecto. La aplicación actualizada usa esa autenticación para iniciar sesión en **toda la aplicación**, incluidos los aportes. Ya no consulta ni guarda contraseñas en la ruta antigua `Usuarios`.

El sitio actualizado con Firebase Authentication está publicado en GitHub Pages. Las reglas actuales de Realtime Database ya bloquean una lectura anónima (HTTP 401). La separación de líderes y asistencias por zona descrita abajo requiere migrar los datos y publicar conjuntamente la versión compatible de la aplicación y las reglas nuevas. El proyecto sigue en Spark y todavía no tiene un bucket para comprobantes.

## Estado actual

La cuenta de Zona1 existe en Authentication y su perfil fue creado con `usuario: "Zona1"`, `rol: "Facilitador"` y `salon: "Zona 1"`. Se usó una regla temporal limitada a esa cuenta y esos valores; la regla fue retirada inmediatamente. Falta que Zona1 pruebe iniciar sesión nuevamente.

## Preparación de cuentas

1. Las cuentas se administran en **Authentication > Users**. La aplicación convierte cada nombre de usuario al correo interno con dominio `@asistencia-iglesia-zonas.firebaseapp.com`.
2. El perfil confirmado de Zona1 en `/Perfiles/{UID de Zona1}` es:

   ```json
   {
     "usuario": "Zona1",
     "rol": "Facilitador",
     "salon": "Zona 1"
   }
   ```

## Aislamiento por zona pendiente de despliegue

La aplicación local y `database.rules.json` se están preparando para usar estas rutas:

- `LideresPorZona/{salon}`
- `AsistenciasPorZona/{salon}`
- `FacilitadoresPorZona/{salon}`
- `DiscipuladoVirtualPorZona/{salonOrigen}`

Cada facilitador leerá únicamente el hijo correspondiente a su `salon`; los administradores y supervisores conservarán la lectura global. Los registros virtuales sin zona de origen y los registros del Pastor quedan disponibles solo para los revisores. La aplicación también borra su caché local al cambiar de usuario para que un navegador compartido no muestre datos de otra zona.

Se preparó `migrar-datos-por-zona.py` para transformar una exportación completa en un archivo que contiene solo las cuatro rutas nuevas. La prueba conservó los 174 líderes, 361 asistencias, 8 facilitadores y 8 registros de discipulado virtual. Las asistencias virtuales se repartieron según su zona de origen cuando existe; las que no tienen zona quedaron bajo `Virtual`.

Antes de aplicar la migración:

1. Exporte la base completa de nuevo y guarde esa copia privada sin compartirla.
2. Ejecute el script apuntando a esa exportación y a un archivo de salida privado:

   ```powershell
   python .\migrar-datos-por-zona.py `
     --source "RUTA\A\EXPORTACION-COMPLETA.json" `
     --output "RUTA\PRIVADA\migracion-por-zona.json"
   ```

3. Revise los totales impresos. Añada únicamente las cuatro rutas nuevas a Firebase, sin sustituir el nodo raíz ni borrar las rutas antiguas.
4. Publique la versión nueva de la aplicación y las reglas de `database.rules.json` en una ventana coordinada. No cierre las rutas compartidas antiguas hasta que los datos nuevos estén cargados y la aplicación nueva esté publicada.
5. Compruebe que un facilitador solo acceda a su zona, que Firebase deniegue el acceso directo a otra zona y que administrador/supervisor puedan revisar todas las zonas.

El archivo de migración contiene información personal y debe mantenerse privado. No lo suba al repositorio ni importe el archivo completo en la raíz de la base: eso podría reemplazar otros datos.

## Alcance de las reglas preparadas

- Sin una cuenta autenticada y un perfil válido en `/Perfiles`, las rutas de datos de la aplicación quedan denegadas. La antigua ruta `Usuarios`, que contenía contraseñas, no se concede a la aplicación.
- Los perfiles no pueden modificarse desde la aplicación; su mantenimiento requiere una operación administrativa.
- Las rutas antiguas de líderes y asistencias siguen existiendo por compatibilidad. El aislamiento de las rutas nuevas no será efectivo en producción hasta migrar los datos, publicar la aplicación compatible y activar las reglas nuevas en el orden indicado arriba.
- Los aportes sí tienen restricciones de servidor: los facilitadores solo pueden crear aportes para su zona y leer los propios; administradores y supervisores pueden revisar todos y cambiar su estado.
- Los comprobantes son imágenes JPG, PNG o WebP de hasta 5 MB. `storage.rules` incluye el UID de Zona1, pero esas reglas no están publicadas y no tendrán efecto hasta crear el bucket.
- La bitácora y los respaldos conservan permisos de revisión. Los respaldos automáticos de cambios realizados por facilitadores ya no se generan; los cambios siguen registrándose en la bitácora.

`database.rules.json` contiene las reglas nuevas preparadas; todavía no se han publicado. `firebase.json` vincula los archivos de reglas para Firebase CLI; el sitio se aloja en GitHub Pages. El propietario autorizó Blaze, pero Firebase Console indica que no existe una cuenta de Cloud Billing disponible para asociar. El propietario debe crear o vincular esa cuenta antes de habilitar Storage, crear el bucket y desplegar `storage.rules`.
