#!/usr/bin/env -S conda run -n cherokee-audio-data python

import shutil

from denoiser.enhance import *
from pydub import AudioSegment

if __name__ == "__main__":

    os.chdir(os.path.dirname(__file__))

    src_noisy: str = os.path.join(os.getcwd(), "src.noisy")
    src_enhanced: str = os.path.join(os.getcwd(), "src")
    src_tmp: str = os.path.join(os.getcwd(), "tmp.src.noisy")

    args = parser.parse_args()

    logging.basicConfig(stream=sys.stderr, level=args.verbose)
    logger.debug(args)

    args.num_workers = 2
    args.out_dir = src_enhanced
    args.noisy_dir = src_tmp

    args.dns48 = True
    # args.dns64 = True
    # args.master64 = True

    # clean up any previous files
    for folder in [src_enhanced, src_tmp]:
        shutil.rmtree(folder, ignore_errors=True)
        os.mkdir(folder)

    # enhance files, one at a time
    audio_files = []
    for (dirpath, dirnames, filenames) in os.walk(src_noisy):
        filename: str
        for filename in filenames:
            if filename.endswith(".mp3"):
                audio_files.append(os.path.join(dirpath, filename))

    audio_files.sort()
    for audio_file in audio_files:
        basename: str = os.path.basename(audio_file)
        print(f" - Processing {basename}")

        audio: AudioSegment = AudioSegment.from_file(audio_file)
        audio = audio.set_channels(1)
        audio = audio.set_frame_rate(16000)
        audio.export(os.path.join(src_tmp, basename + ".wav"), format="wav")

        enhance(args, local_out_dir=args.out_dir)

        audio = AudioSegment.from_file(os.path.join(src_enhanced, basename + "_enhanced.wav"))
        audio = audio.set_channels(1)
        audio = audio.set_frame_rate(22050)
        audio.export(os.path.join(src_enhanced, basename), format="mp3", parameters=["-qscale:a", "2"])

        os.remove(os.path.join(src_tmp, basename + ".wav"))
        os.remove(os.path.join(src_enhanced, basename + "_noisy.wav"))
        os.remove(os.path.join(src_enhanced, basename + "_enhanced.wav"))

    shutil.rmtree(src_tmp, ignore_errors=True)

    print()
    print("DONE")
    print()
