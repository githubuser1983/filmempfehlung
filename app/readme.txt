android update project --target 3 --path .

# debug:
adb logcat | grep "mobeta"

# install
adb install -r bin/DemoDSLV-debug.apk

# compile
ant debug
ant release

# sign:
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore my-release-key.keystore bin/Filmempfehlung-release-unsigned.apk alias_name

# zipalign
zipalign -v 4 bin/Filmempfehlung-release-unsigned.apk bin/Filmempfehlung-release-signed.apk

# todo:
# 1. Drehung vertikal / horizontal erzeugt neue Filme -> rausnehmen
# 2. Knopf (anstelle von Hilfe) um neue Filme zum sortieren anzuzeigen
# 3. Zustandspeicherung: Wenn Benutzer die App verlaesst und wieder aufmacht sollte er sich im letzten Zustand wiederfinden.
# 4. Roter X - Knopf zum Loeschen von Filmen
# (5. Speichern von vorgeschlagenen Filmlisten)
# 6. Senden der Filme, die der User weggeklickt hat an den Server
# 7. Einstellungen (z.B. Anzahl der Filme die vorgeschlagen werden: 50,100,200; Nur Filme die ich nicht kenne vorschlagen, Sowohl Filme die ich kenne als auch Filme die ich nicht kenne vorschlagen; IP-Adresse des Servers; Benutzername?)
