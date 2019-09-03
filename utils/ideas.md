#### for WIT

- [x] simple mad libs, perhaps with different voice
- [ ] face training/recognition:
    - [ ] improve on challenge
    - [x] have misty search for people
    - [ ] say hi to them as they walk by
- [x] internet test
    - [x] use wifi/cellular from usb-tethered phone
- [x] generic/easy import file
    - `from utils.misty import *`

##### to bring:
- [ ] misty
- [ ] macbook
- [ ] chargers
    - [ ] phone
    - [ ] macbook
    - [ ] misty
- [ ] power strip or 2
- [ ] extension cord
- [ ] hdmi cable
- [ ] raspberry pi?



##### ideas
- [ ] simple dialogue flow to determine yes or no
- [ ] grab seats from database and say hello in all languages
- [x] create a keyboard reader
- [ ] youtube to mp3: https://mp3converter.to
- [ ] text doc of all things to say at WIT



config for tts audio for misty:
```
        {
          "audioConfig": {
            "audioEncoding": "LINEAR16",
            "pitch": 2,
            "speakingRate": 1
          },
          "input": {
            "text": "hi, i'm co-pi-lette"
          },
          "voice": {
            "languageCode": "en-US",
            "name": "en-US-Wavenet-E"
          }
        }
```
