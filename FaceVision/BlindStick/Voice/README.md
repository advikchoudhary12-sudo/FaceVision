Place the MP3 voice prompts for the blind-stick feature in this folder.
Filenames default to the recognized person label, such as `Ayan.mp3`. The
`DEFAULT_VOICE_FILE` setting in `local_settings.py` selects the generic prompt
used when V10 activates but no face is detected, or when no identity-specific
file exists. It should be just a filename in this folder. `unknown.mp3` is the
default generic prompt and is also used for detected but unrecognized faces
unless overridden. Local MP3 files are ignored by Git.
