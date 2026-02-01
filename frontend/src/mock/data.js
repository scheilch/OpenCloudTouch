// Mock Data for Swipe SPA Prototype

export const MOCK_DEVICES = [
  {
    device_id: "aabbcc112233",
    name: "Wohnzimmer ST30",
    model: "SoundTouch 30 Series III",
    ip: "192.0.2.101",
    firmware: "27.0.6.24430.3672456",
    mac_address: "AA:BB:CC:11:22:33",
    capabilities: {
      presets: true,
      now_playing: true,
      volume: true,
      zones: true,
      hdmi: false,
      bluetooth: true
    }
  },
  {
    device_id: "ddeeff445566",
    name: "Küche ST10",
    model: "SoundTouch 10",
    ip: "192.0.2.102",
    firmware: "26.0.12.14830.2145678",
    mac_address: "DD:EE:FF:44:55:66",
    capabilities: {
      presets: true,
      now_playing: true,
      volume: true,
      zones: true,
      hdmi: false,
      bluetooth: true
    }
  },
  {
    device_id: "112233aabbcc",
    name: "Soundbar ST300",
    model: "SoundTouch 300",
    ip: "192.0.2.103",
    firmware: "28.0.5.27321.4123456",
    mac_address: "11:22:33:AA:BB:CC",
    capabilities: {
      presets: true,
      now_playing: true,
      volume: true,
      zones: true,
      hdmi: true,
      bluetooth: true
    }
  }
];

export const MOCK_RADIO_STATIONS = [
  {
    stationuuid: "96062a7c-0601-11e8-ae97-52543be04c81",
    name: "Absolut relax",
    url: "http://stream.absolut-relax.de/relax/mp3-128/stream.absolut-relax.de/",
    country: "Germany",
    countrycode: "DE",
    language: "german",
    codec: "MP3",
    bitrate: 128,
    homepage: "https://www.absolut-relax.de",
    favicon: "https://www.absolut-relax.de/favicon.ico",
    tags: "chillout,lounge,relax"
  },
  {
    stationuuid: "96062af1-0601-11e8-ae97-52543be04c81",
    name: "Bayern 1",
    url: "http://streams.br.de/bayern1_2.m3u",
    country: "Germany",
    countrycode: "DE",
    language: "german",
    codec: "AAC",
    bitrate: 96,
    homepage: "https://www.br.de/radio/bayern1/",
    favicon: "https://www.br.de/favicon.ico",
    tags: "pop,news,talk"
  },
  {
    stationuuid: "e8f96462-cea0-4c44-8bb0-ddeeff889900",
    name: "1LIVE",
    url: "https://wdr-1live-live.icecastssl.wdr.de/wdr/1live/live/mp3/128/stream.mp3",
    country: "Germany",
    countrycode: "DE",
    language: "german",
    codec: "MP3",
    bitrate: 128,
    homepage: "https://www1.wdr.de/radio/1live/",
    favicon: "https://www1.wdr.de/favicon.ico",
    tags: "pop,rock,electronic"
  },
  {
    stationuuid: "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    name: "SWR3",
    url: "https://swr-swr3-live.cast.addradio.de/swr/swr3/live/mp3/128/stream.mp3",
    country: "Germany",
    countrycode: "DE",
    language: "german",
    codec: "MP3",
    bitrate: 128,
    homepage: "https://www.swr3.de",
    favicon: "https://www.swr3.de/favicon.ico",
    tags: "pop,rock,charts"
  },
  {
    stationuuid: "b2c3d4e5-f6g7-8901-bcde-f12345678901",
    name: "Deutschlandfunk",
    url: "https://st01.sslstream.dlf.de/dlf/01/high/aac/stream.aac",
    country: "Germany",
    countrycode: "DE",
    language: "german",
    codec: "AAC",
    bitrate: 128,
    homepage: "https://www.deutschlandfunk.de",
    favicon: "https://www.deutschlandfunk.de/favicon.ico",
    tags: "news,talk,culture"
  }
];

export const MOCK_NOW_PLAYING = {
  device_id: "aabbcc112233",
  source: "INTERNET_RADIO",
  station: "Absolut relax",
  artist: "",
  album: "",
  track: "Chillout Lounge Mix",
  art_url: "https://via.placeholder.com/500x500/0066CC/FFFFFF?text=Absolut+relax",
  play_status: "PLAY_STATE",
  volume: 45,
  duration: 0,
  position: 0
};

export const MOCK_PRESET_MAPPING = {
  "aabbcc112233": {
    1: {
      station_uuid: "96062a7c-0601-11e8-ae97-52543be04c81",
      station_name: "Absolut relax",
      station_url: "http://stream.absolut-relax.de/relax/mp3-128/stream.absolut-relax.de/"
    },
    2: {
      station_uuid: "96062af1-0601-11e8-ae97-52543be04c81",
      station_name: "Bayern 1",
      station_url: "http://streams.br.de/bayern1_2.m3u"
    },
    3: null,
    4: null,
    5: null,
    6: null
  },
  "ddeeff445566": {
    1: {
      station_uuid: "e8f96462-cea0-4c44-8bb0-ddeeff889900",
      station_name: "1LIVE",
      station_url: "https://wdr-1live-live.icecastssl.wdr.de/wdr/1live/live/mp3/128/stream.mp3"
    },
    2: null,
    3: null,
    4: null,
    5: null,
    6: null
  },
  "112233aabbcc": {
    1: null,
    2: null,
    3: null,
    4: null,
    5: null,
    6: null
  }
};
