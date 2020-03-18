## for tile lights
- conway game of life
- arkanoid
- flip through images


#### for demo:

- [x] fix misty's sounds/moods
- [x] fix train face - test with lower volume?
- [ ] calibrate misty

- to demo:
    - audio:
        - [ ] say
        - [ ] play
    - movement
        - [ ] search?
        - [ ] nod?
        - [ ] shake_head?
    - touch
        - [ ] respond to touch
    - compose
        - [ ] smooth_jazz
        - [ ] party_mode
        - [ ] lets_get_silly
    - [ ] train_face
    - [ ] `from utils.misty.routines.identify import run` 
- to discuss:
    - i wrote the API i'm using
    - i got to use a field trial version
    - they out to interview me
    - dialogflow - for conversations with xaxis traders
    - CES: recognizing faces and saying hello
    - CES: responding to questions about schedule
    - CES: mistyrobotics will be there and are willing to help out
    and they interviewed me at my place
    
- concerns with interaction (from kelley email):
    - volume (use a bluetooth connected speaker)
    - keyphrase (might be too loud - instead respond to touch?)
    - recording audio (workaround discovered - lower the volume to around 50)

#### bugs
- [ ] add `ignore` to `reset_to_orig`
- [ ] can't set both arm positions simultaneously, for some reason


#### for WIT

- [x] simple mad libs, perhaps with different voice
- [x] face training/recognition:
    - [x] improve on challenge
    - [x] have misty search for people
    - [ ] say hi to them as they walk by
- [x] internet test
    - [x] use wifi/cellular from usb-tethered phone
- [x] generic/easy import file
    - `from utils.misty import *`

##### to bring:
- [x] misty
- [x] macbook
- [x] chargers
    - [x] phone
    - [x] macbook
    - [x] misty
- [x] power strip or 2
- [ ] extension cord
- [x] hdmi cable
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
