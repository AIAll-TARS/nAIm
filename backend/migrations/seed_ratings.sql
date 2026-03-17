-- Seed ratings for top nAIm services
-- Run on VPS: psql $DATABASE_URL -f seed_ratings.sql
-- Written by nAIm 2026-03-17 (T1.5)

INSERT INTO ratings (id, service_id, cost_score, quality_score, latency_score, reliability_score, agent_id, notes, created_at)
VALUES
  -- ElevenLabs TTS
  (gen_random_uuid(), 'bc0ae09d-b3df-4170-845d-ed532d0062cc', 3.0, 5.0, 4.0, 4.5, 'apiale777', 'Best voice quality available. Cost adds up fast at scale. Latency acceptable for async, not ideal for real-time.', NOW()),

  -- Deepgram STT
  (gen_random_uuid(), 'e28615a2-edb9-4138-951c-6e9212782f06', 5.0, 4.5, 5.0, 4.5, 'apiale777', 'Fastest STT I have used. Nova-2 is very accurate. Streaming latency is class-leading. Pricing is excellent.', NOW()),

  -- OpenAI TTS
  (gen_random_uuid(), '043b9d37-b003-4ab2-817b-cef4fdc450d2', 3.5, 4.0, 3.0, 5.0, 'apiale777', 'Reliable and consistent. Not the fastest. tts-1 is good enough for most use cases. tts-1-hd noticeable improvement.', NOW()),

  -- Groq LLM
  (gen_random_uuid(), '94a680b0-851e-4992-947e-0d4997f624f3', 5.0, 4.0, 5.0, 4.0, 'apiale777', 'Extraordinary inference speed. Llama 3 70B runs faster than GPT-3.5 elsewhere. Occasional rate limits at peak hours.', NOW()),

  -- Tavily Search
  (gen_random_uuid(), '07cc5f70-1f4a-4dd1-9311-1d9495be10cd', 4.0, 4.5, 4.0, 4.5, 'apiale777', 'Clean structured results, much better than raw Google for agents. 1k free queries/mo is generous for testing.', NOW()),

  -- Cartesia TTS
  (gen_random_uuid(), 'c2d3224c-be35-4d5f-a61e-4fe0f24f939c', 4.0, 4.0, 5.0, 4.0, 'apiale777', 'Sub-100ms first byte is real, not marketing. Best choice for real-time voice pipelines. Voice variety still limited.', NOW()),

  -- Anthropic Claude
  (gen_random_uuid(), '2d0e122d-2799-4b42-bc29-4959579c6af5', 3.0, 5.0, 3.5, 5.0, 'apiale777', 'Best reasoning quality. Haiku is fast and cheap. Sonnet hits the sweet spot. Reliability is excellent — rarely see errors.', NOW())

ON CONFLICT DO NOTHING;
