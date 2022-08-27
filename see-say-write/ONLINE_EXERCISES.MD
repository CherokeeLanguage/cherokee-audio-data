# Online exercises for see-say-write

To add new vocab:

1. Add new rows to `online-exercises-data.csv` with syllabary, english, and "simplified" phonetics (no tone, vowel length, or glottal stops). The audio column should be left blank.
2. Run `match_audio_files.py`. This will search the tagged audio for matching phonetics for each row and give you a list of options.
3. Enter the index of the option to select it and associate the audio file with the term. If there is no matching audio, simply press "Enter."
4. `ssw.zip` can be moved into the online exercises project. The JSON files live in `src/collections` and the audio lives in `public/`.
