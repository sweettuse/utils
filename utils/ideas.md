#### for WIT

- [x] simple mad libs, perhaps with different voice
- [ ] face training/recognition:
    - [ ] improve on challenge
    - [ ] have misty search for people
    - [ ] say hi to them as they walk by
- [ ] internet test
    - [ ] use wi-fi from ipad, share that from macbook, log misty in
- [ ] generic/easy import file

##### to bring:
- [ ] phone charger
- [ ] macbook charger
- [ ] ipad cables
- [ ] power strip or 2
- [ ] hdmi cable
- [ ] raspberry pi?



##### ideas
- [ ] simple dialogue flow to determine yes or no!
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
