#!/bin/sh
set -eu
cd -- "$(dirname -- "$0")"
if ! /usr/bin/python3 -c 'import gi, cairo; gi.require_version("Gtk", "3.0"); from gi.repository import Gtk' 2>/dev/null; then
    echo 'Install Python 3, GTK 3, PyGObject and Cairo first. See README.md.' >&2
    exit 1
fi
exec /usr/bin/python3 binary_watch.py "$@"
