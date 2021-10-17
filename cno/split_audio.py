#!/usr/bin/env python3
import dataclasses
import json
import os
import sys
from builtins import list
from os import walk
from shutil import rmtree

from pydub import AudioSegment
from pydub.effects import normalize


def detect_sound(sound: AudioSegment, silence_threshold: float = -55.0, chunk_size: int = 150) -> list:
    """
    sound is a pydub.AudioSegment
    silence_threshold in dB
    chunk_size in ms
    iterate over entire AudioSegment looking for non-silent chunks
    returns list of chunks as a list of tuples (begin, end). In milliseconds.
    returns an empty list of no sound chunks found
    """
    sound_start: int = -1
    segments: list = list()

    segment_mid: int = len(sound)
    for position in range(0, len(sound), 10):  # process in 10 ms chunks
        segment_end: int = min(position + chunk_size, len(sound))
        segment_mid = min(int(position + chunk_size / 2), len(sound))
        nextChunk: AudioSegment = sound[position:segment_end]
        if sound_start < 0 and nextChunk.dBFS <= silence_threshold:
            continue
        if sound_start < 0:
            if position == 0:
                sound_start = 0
            else:
                sound_start = segment_mid
            continue
        if sound_start >= 0 and nextChunk.dBFS <= silence_threshold:
            segments.append((sound_start, segment_mid))
            sound_start = -1
            continue

    if sound_start >= 0:
        segments.append((sound_start, segment_mid))

    if len(segments) == 0:
        segments.append((0, len(sound)))

    return segments


def combine_segments(segments: list, gap_break_duration: int, target_length: int) -> list:
    new_segments: list = list()

    if len(segments) == 0:
        return list()

    if len(segments) == 1:
        new_segments.append(segments[0])
        return new_segments

    (start, end) = segments[0]

    this_start: int
    this_end: int
    for ix in range(1, len(segments)):
        (this_start, this_end) = segments[ix]
        if this_start - end < gap_break_duration and this_end - start < target_length:
            end = this_end
            continue
        new_segments.append((start, end))
        start = this_start
        end = this_end

    if not new_segments or start != new_segments[-1]:
        new_segments.append((start, end))

    return new_segments


def main():
    split_config: SplitConfig = SplitConfig()
    split_config.load("split_config.json")

    silence_threshold: float = split_config.silence_threshold
    silence_min_duration: int = split_config.silence_min_duration
    max_target_duration: int = split_config.max_target_duration
    gap_break_duration: int = split_config.gap_break_duration

    if sys.argv[0]:
        workdir: str = os.path.dirname(sys.argv[0])
        if workdir:
            os.chdir(workdir)
    workdir = os.getcwd()

    # clean up any previous files
    rmtree("mp3", ignore_errors=True)
    os.mkdir("mp3")

    audio_files = []
    for (dir_path, dir_names, filenames) in walk("src"):
        for filename in filenames:
            audio_files.append(os.path.join(dir_path, filename))
    print(f"Found {len(audio_files):,} audio files for processing")
    audio_files.sort()
    splits: list = []
    tix: int = 1
    min_length: float = -1.0
    max_length: float = 0.0
    total_length: float = 0.0
    for audio_file in audio_files:
        ext: str = os.path.splitext(audio_file)[1].lower()
        if ext not in [".mp3", ".wav"]:
            continue

        data: AudioSegment = AudioSegment.from_file(audio_file).set_channels(1)
        data = normalize(data)

        segments = detect_sound(data, silence_threshold, silence_min_duration)
        segments = combine_segments(segments, gap_break_duration, max_target_duration)

        if len(segments) == 0:
            print(f"=== ONLY SILENCE FOUND IN: {audio_file}")
            continue

        for segment_start, segment_end in segments:
            if "/" in audio_file:
                audio_file = audio_file[audio_file.rfind("/") + 1:]

            # Normalize the chunk.
            normalized: AudioSegment = normalize(data[segment_start:segment_end])

            # If it is very short, it's probably just noise, skip it
            if normalized.duration_seconds < 0.25:
                continue

            chunk_mp3 = f"{tix:04d}-{audio_file}".replace("/", "_").replace(" ", "_").replace("__", "_")
            chunk_mp3 = os.path.splitext(chunk_mp3)[0]
            output_file = f"mp3/{chunk_mp3}-{int(segment_start):06d}.mp3"
            tix += 1
            print(f"Saving {output_file}.")
            normalized.export(output_file, format="mp3", parameters=["-qscale:a", "0"])
            splits.append(output_file)

            duration: float = normalized.duration_seconds
            total_length += duration
            if min_length < 0 or min_length > duration:
                min_length = duration
            if max_length < duration:
                max_length = duration

    work_folder: str = os.path.basename(workdir)
    msg: str = "\n"
    msg += f"Work directory: {work_folder}\n"
    msg += "\n"
    msg += f"Total splits: {len(splits):,}\n"
    msg += "\n"
    msg += f"Min duration: {min_length:,.02f} seconds\n"
    msg += f"Max duration: {max_length:,.02f} seconds\n"
    msg += f"Total duration: {total_length:,.02f} seconds\n"
    msg += "\n"

    with open("split_audio-stats.txt", "w") as f:
        f.write(msg)
    print(msg)

    sys.exit()


@dataclasses.dataclass
class SplitConfig:
    silence_threshold: float = -40.0
    silence_min_duration: int = 250  # 225  # ms
    max_target_duration: int = 10000  # ms
    gap_break_duration: int = 750  # 675  # ms

    def load(self, config_file: str):
        config: dict
        if not os.path.exists(config_file):
            self.save(config_file)
            return

        try:
            with open(config_file, "r") as r:
                config = json.load(r)
        except json.JSONDecodeError:
            self.save(config_file)
            return
        if type(config) == dict:
            for k, v in config.items():
                setattr(self, k, v)
        else:
            self.save(config_file)

    def save(self, config_file: str):
        with open(config_file, "w") as w:
            json.dump(dataclasses.asdict(self), w, indent=4)


if __name__ == "__main__":
    main()
