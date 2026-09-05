# SATYA Field Capture (Android)

React Native (Expo SDK 57) mobile app for field engineers. Implements the
"Field Capture App" from the SIH deck: log observation, capture photo, voice
note, offline queue, sync to the SATYA backend.

## What it does

- **Log tab**: event type, discipline, optional Activity ID, location/chainage,
  quantity + unit, free-text description, camera photo, voice recording.
  Saved locally (AsyncStorage) so it works with no network.
- **Queue tab**: every observation with PENDING / SYNCED / FAILED status.
  "Sync now" POSTs each pending item to `POST /api/v1/ingestion/upload` as a
  DPR-style sentence the backend extractor understands
  (e.g. `ACT-1010: Trenching completed 500 Meters at Section 1, Km 0.0 to 2.0.`).
  The backend then runs extraction, matching, trust evaluation and projection.
  Long-press an item to delete it.
- **Settings tab**: backend URL, project ID, author. "Test connection" hits
  `/api/v1/health`.

## Run in development

```
npm install
npx expo start          # then press "a" for the Android emulator / device
```

Start the backend on your PC first:

```
python scripts/run_server.py
```

On an emulator the default URL `http://10.0.2.2:8000` reaches the PC. On a real
phone, set the URL in Settings to your PC's LAN IP (both on the same Wi-Fi).

## Build the APK

Requires Android SDK and a JDK 17+. Android Studio's bundled JDK works:

```
set JAVA_HOME=C:\Program Files\Android\Android Studio\jbr
cd android
gradlew.bat assembleRelease
```

Output: `android/app/build/outputs/apk/release/app-release.apk`
(signed with the debug keystore, fine for demos and sideloading).

Install on a connected phone with `adb install -r app-release.apk`.
