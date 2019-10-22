import os
from tempfile import NamedTemporaryFile
from subprocess import run, Popen, PIPE

__author__ = 'acushner'

out = '/sdcard/audio/Audio'


def upload_audio_to_misty(d):
    """
    misty has a 3mb upload limit on audio files. this works around that.

    give it a directory where your audio files are organized into folders,
    and this will automatically upload them to misty using adb (android debug bridge).


    it prepends folders to the name so the files are organized nicely on misty herself:
        - ./music/mario/super_mario_theme.mp3 -> music--mario--super_mario_theme.mp3

    sample commands:
        adb connect 192.168.86.24:5555
        adb push "./silence_stop.mp3" "/sdcard/audio/Audio/silence_stop.mp3"
        adb push "./misc/smooth_jazz_will_be_deployed.mp3" "/sdcard/audio/Audio/misc--smooth_jazz_will_be_deployed.mp3"


    NOTE: reboot misty after the upload is complete so she can recognize the new files
    """

    os.chdir(d)
    commands = [f'adb connect {os.environ["MISTY_IP"]}:5555']
    for path, _, files in os.walk('.'):
        for f in files:
            local_fn = f'{path}/{f}'
            target_fn = local_fn[2:].replace('/', '--')
            commands.append(f'adb push "{local_fn}" "{out}/{target_fn}"')

    command_str = '\n'.join(commands)
    with NamedTemporaryFile('w') as f:
        f.write(command_str)
        f.flush()
        res = run(f'. {f.name}', shell=True, check=True, capture_output=True)
        print(res.stdout.decode())


def __main():
    upload_audio_to_misty('your directory here')


if __name__ == '__main__':
    __main()
