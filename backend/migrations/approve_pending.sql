-- Approve google-cloud-tts and azure-speech-tts (added 2026-03-13, stuck as pending)
UPDATE services SET status='approved' WHERE slug IN ('google-cloud-tts', 'azure-speech-tts');
