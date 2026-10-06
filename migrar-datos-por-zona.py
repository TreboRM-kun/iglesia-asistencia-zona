import argparse
import json
import unicodedata
from collections import defaultdict
from pathlib import Path


def filas_de(raiz):
    if isinstance(raiz, list):
        return raiz
    if isinstance(raiz, dict):
        return list(raiz.values())
    return []


def salon_normalizado(valor):
    salon = str(valor or "").strip()
    return "Virtual" if salon == "Zona 7" else salon


def normalizar_nombre(valor):
    texto = unicodedata.normalize("NFD", str(valor or "").strip())
    sin_acentos = "".join(
        caracter for caracter in texto
        if not unicodedata.combining(caracter)
    )
    return sin_acentos.casefold()


def agrupar(registros, obtener_salon, nombre_raiz):
    grupos = defaultdict(list)
    for numero, fila in enumerate(registros, start=1):
        if not isinstance(fila, dict):
            raise ValueError(f"{nombre_raiz}: el registro {numero} no es un objeto.")
        salon = salon_normalizado(obtener_salon(fila))
        if not salon:
            raise ValueError(f"{nombre_raiz}: el registro {numero} no tiene zona.")
        grupos[salon].append(fila)
    return dict(grupos)


def transformar(datos):
    filas_lideres = filas_de(datos.get("LideresIglesiaRedencionV2"))
    filas_asistencias = filas_de(datos.get("AsistenciasIglesiaRedencionV2"))
    filas_facilitadores = filas_de(datos.get("Facilitadores"))
    filas_virtuales = filas_de(
        datos.get("DiscipuladoVirtualIglesiaRedencionV2")
    )

    origenes_virtuales = {
        normalizar_nombre(fila.get("Nombre")):
            salon_normalizado(fila.get("SalonOrigen"))
        for fila in filas_virtuales
        if isinstance(fila, dict) and fila.get("Nombre")
    }

    def salon_asistencia(fila):
        if fila.get("TipoReunion") == "Discipulado Virtual":
            origen = origenes_virtuales.get(
                normalizar_nombre(fila.get("Nombre"))
            )
            if origen:
                return origen
        return fila.get("Salon")

    migrados = {
        "LideresPorZona": agrupar(
            filas_lideres, lambda fila: fila.get("Salon"), "Líderes"
        ),
        "AsistenciasPorZona": agrupar(
            filas_asistencias, salon_asistencia, "Asistencias"
        ),
        "FacilitadoresPorZona": agrupar(
            filas_facilitadores, lambda fila: fila.get("Salon"), "Facilitadores"
        ),
        "DiscipuladoVirtualPorZona": agrupar(
            filas_virtuales, lambda fila: fila.get("SalonOrigen"), "Discipulado virtual"
        ),
    }

    esperados = {
        "LideresPorZona": len(filas_lideres),
        "AsistenciasPorZona": len(filas_asistencias),
        "FacilitadoresPorZona": len(filas_facilitadores),
        "DiscipuladoVirtualPorZona": len(filas_virtuales),
    }
    for raiz, cantidad in esperados.items():
        actual = sum(map(len, migrados[raiz].values()))
        if actual != cantidad:
            raise ValueError(f"{raiz}: se esperaban {cantidad} filas y hay {actual}.")
    return migrados


def resumen(migrados):
    for raiz, zonas in migrados.items():
        conteos = dict(sorted(
            (zona, len(filas)) for zona, filas in zonas.items()
        ))
        total = sum(conteos.values())
        print(f"{raiz}: {total} registros; por zona: {conteos}")


def main():
    parser = argparse.ArgumentParser(
        description="Prepara una copia de los datos existentes particionada por zona."
    )
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.source.resolve() == args.output.resolve():
        raise SystemExit("El archivo de origen no puede usarse como archivo de salida.")
    if args.output.exists() and not args.force:
        raise SystemExit(
            f"El archivo de salida ya existe: {args.output}. "
            "Use --force solo si desea reemplazarlo."
        )
    with args.source.open("r", encoding="utf-8") as archivo:
        datos = json.load(archivo)
    migrados = transformar(datos)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporal = args.output.with_suffix(args.output.suffix + ".tmp")
    with temporal.open("w", encoding="utf-8", newline="\n") as archivo:
        json.dump(migrados, archivo, ensure_ascii=False, separators=(",", ":"))
        archivo.write("\n")
    temporal.replace(args.output)
    print(f"Archivo de migración validado: {args.output}")
    resumen(migrados)


if __name__ == "__main__":
    main()
