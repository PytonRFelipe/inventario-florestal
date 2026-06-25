[app]
title = Inventario Florestal
package.name = inventarioapp
package.domain = org.seuusuario
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

# CORREÇÃO: Alinhado para usar as receitas nativas e estáveis do buildozer
requirements = python3, kivy, android

orientation = portrait
fullscreen = 1

# CORREÇÃO ANDROID 14: Deixamos apenas INTERNET. Como o main.py usa armazenamento
# interno/isolado (getFilesDir/getExternalFilesDir), as permissões de STORAGE são dispensáveis e obsoletas.
android.permissions = INTERNET

android.api = 34
android.minapi = 21

# RECOMENDAÇÃO: Deixar essas duas linhas comentadas (com #) faz o Buildozer buscar 
# automaticamente a versão ideal do NDK no GitHub Actions, evitando quebras por desalinhamento.
# android.ndk = 26b
# android.ndk_api = 21

android.archs = arm64-v8a
android.accept_sdk_license = True
