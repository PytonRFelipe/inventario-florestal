[app]
title = Inventario Florestal
package.name = inventarioapp
package.domain = org.seuusuario
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

# CORREÇÃO: Incluído o 'android' nos requisitos para permitir acesso ao sistema do celular
requirements = python3, kivy, android

orientation = portrait
fullscreen = 1

# CORREÇÃO: Adicionadas as permissões para leitura e escrita de arquivos
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

android.api = 34
android.minapi = 21
android.ndk = 26b
android.ndk_api = 21
android.archs = arm64-v8a
android.accept_sdk_license = True
