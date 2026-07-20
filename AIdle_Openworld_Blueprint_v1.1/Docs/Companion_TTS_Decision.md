# Companion TTS decision — 2026-07-20

Status: `DEFERRED_POST_ALPHA / TEXT_ONLY_MVP`

| Candidate | Current route | Reason |
|---|---|---|
| OpenVoice V2 | adapter benchmark | permissive claim, but no native Vietnamese base TTS and Windows path is unofficial |
| StyleTTS 2 | R&D only | research-oriented stack and complex checkpoint/dependency licensing |
| Coqui toolkit | toolkit evaluation | toolkit license does not grant every model license |
| XTTS-v2 checkpoint | commercial block | current checkpoint license is non-commercial and language list lacks Vietnamese |

No candidate is an MVP dependency. A future production contract would be
provider-neutral and asynchronous. It accepts text,
locale, bounded response style and prosody; it returns audio plus model, voice,
license, latency and consent receipts. Raw private memory is never sent to TTS.

Voice enrollment/cloning, raw-audio retention and commercial checkpoint selection
require Human approval and market-specific legal review.

Primary sources:
[OpenVoice](https://github.com/myshell-ai/OpenVoice),
[StyleTTS 2](https://github.com/yl4579/StyleTTS2),
[maintained Coqui fork](https://github.com/idiap/coqui-ai-TTS), and
[XTTS-v2 license](https://huggingface.co/coqui/XTTS-v2/blob/main/LICENSE.txt).
