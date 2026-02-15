# Test Results - Preset Playback Comparison

**Date**: 2026-02-14 18:20  
**Device**: Küche (689E194F7D2F)

---

## ❌ PRESET 1: INTERNET_RADIO (Direct Stream URL) - FAILS

**Preset Configuration:**
```xml
<ContentItem 
  source="INTERNET_RADIO" 
  location="https://edge71.live-sm.absolutradio.de/absolut-relax/stream/mp3">
  <itemName>Absolut Relax (Direct)</itemName>
</ContentItem>
```

**Result:** `INVALID_SOURCE` - No playback

---

## ✅ PRESET 4: TUNEIN (Absolut relax) - WORKS PERFECTLY

**Preset Configuration:**
```xml
<ContentItem 
  source="TUNEIN" 
  location="/v1/playback/station/s158432">
  <itemName>Absolut relax</itemName>
</ContentItem>
```

**Now Playing Response:**
```xml
<nowPlaying source="TUNEIN" sourceAccount="">
  <ContentItem source="TUNEIN" type="stationurl" 
               location="/v1/playback/station/s158432">
    <itemName>Absolut relax</itemName>
    <containerArt>http://cdn-profiles.tunein.com/s158432/images/logog.png</containerArt>
  </ContentItem>
  <track>Absolut relax</track>
  <artist>Entspannt durch den Tag</artist>
  <stationName>Absolut relax</stationName>
  <playStatus>PLAY_STATE</playStatus>   ← PLAYING!
  <streamType>RADIO_STREAMING</streamType>
</nowPlaying>
```

---

## Conclusion

**SAME STATION, DIFFERENT SOURCE:**
- Via TuneIn: ✅ WORKS
- Via Direct URL: ❌ FAILS

**Root Cause:** Bose SoundTouch devices do NOT support direct `INTERNET_RADIO` + HTTPS stream URLs

**Solution:** Implement OCT Backend Proxy (Original Plan from Iteration 3)
- Preset points to: `http://192.168.178.108:7777/stations/preset/1`
- OCT Backend handles stream resolution
- Bose treats OCT like "TuneIn integration"
