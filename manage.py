#!/usr/bin/env python
"""Utility a riga di comando di Django per amministrare il progetto."""
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ristorante_project.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Impossibile importare Django. Controlla che sia installato "
            "e disponibile nella tua variabile d'ambiente PYTHONPATH. "
            "Hai dimenticato di attivare l'ambiente virtuale?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
