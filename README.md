# bulk-transcript

Local YouTube bulk transcript workflow.

Goal:
- accept a CSV or TXT file of YouTube URLs
- prefer captions first
- fall back to local Whisper when needed
- save one transcript per video
- save one combined transcript file
- keep resumable status logs
- work on Windows
