[app]
title = Inventario Florestal
package.name = inventarioapp
package.domain = org.seuusuario
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

# NOTA: Adicione aqui dentro, separadas por vírgula, outras bibliotecas que seu main.py use.
# Exemplo: python3, kivy, pandas, openpyxl
requirements = python3, kivy

orientation = portrait
fullscreen = 1
android.permissions = INTERNET
android.api = 34
android.minapi = 21
android.ndk = 26b
android.ndk_api = 21
android.archs = arm64-v8a
android.accept_sdk_license = True
