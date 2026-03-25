"""
Google Speech-to-Text Adapter — implements TranscriptionPort.

Architectural Intent:
- Wraps Google Cloud Speech-to-Text with speaker diarization
- Maps diarization results to domain TranscriptSegment entities
- Graceful degradation if SDK not installed
"""

from staff_echo.domain.entities.transcript import TranscriptSegment
from staff_echo.domain.value_objects.speaker import Speaker, SpeakerRole

try:
    from google.cloud import speech

    _HAS_SPEECH = True
except ImportError:
    _HAS_SPEECH = False


class GoogleSTTAdapter:

    def __init__(self, project_id: str = ""):
        self._project_id = project_id
        self._client = None
        if _HAS_SPEECH and project_id:
            self._client = speech.SpeechClient()

    async def transcribe(self, audio_source: str) -> list[TranscriptSegment]:
        if not self._client:
            return self._dev_fallback(audio_source)

        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            language_code="en-US",
            enable_automatic_punctuation=True,
            diarization_config=speech.SpeakerDiarizationConfig(
                enable_speaker_diarization=True,
                min_speaker_count=2,
                max_speaker_count=2,
            ),
        )
        audio = speech.RecognitionAudio(uri=audio_source)
        response = self._client.recognize(config=config, audio=audio)

        segments: list[TranscriptSegment] = []
        for result in response.results:
            alt = result.alternatives[0]
            for word_info in alt.words:
                speaker_tag = word_info.speaker_tag
                role = SpeakerRole.STAFF if speaker_tag == 1 else SpeakerRole.CUSTOMER
                speaker = Speaker(
                    id=f"speaker_{speaker_tag}",
                    name=f"Speaker {speaker_tag}",
                    role=role,
                )
                segments.append(
                    TranscriptSegment(
                        speaker=speaker,
                        text=word_info.word,
                        start_time=word_info.start_time.total_seconds(),
                        end_time=word_info.end_time.total_seconds(),
                    )
                )
        return self._merge_segments(segments)

    @property
    def supports_diarization(self) -> bool:
        return True

    def _merge_segments(
        self, word_segments: list[TranscriptSegment]
    ) -> list[TranscriptSegment]:
        if not word_segments:
            return []
        merged: list[TranscriptSegment] = []
        current_speaker = word_segments[0].speaker
        current_words: list[str] = [word_segments[0].text]
        start = word_segments[0].start_time

        for seg in word_segments[1:]:
            if seg.speaker.id == current_speaker.id:
                current_words.append(seg.text)
            else:
                merged.append(
                    TranscriptSegment(
                        speaker=current_speaker,
                        text=" ".join(current_words),
                        start_time=start,
                        end_time=seg.start_time,
                    )
                )
                current_speaker = seg.speaker
                current_words = [seg.text]
                start = seg.start_time

        if current_words:
            merged.append(
                TranscriptSegment(
                    speaker=current_speaker,
                    text=" ".join(current_words),
                    start_time=start,
                    end_time=word_segments[-1].end_time,
                )
            )
        return merged

    def _dev_fallback(self, audio_source: str) -> list[TranscriptSegment]:
        staff = Speaker(id="speaker_1", name="Staff Member", role=SpeakerRole.STAFF)
        customer = Speaker(id="speaker_2", name="Customer", role=SpeakerRole.CUSTOMER)
        return [
            TranscriptSegment(speaker=customer, text="Hi, I'm looking for pricing on your services.", start_time=0.0, end_time=3.0),
            TranscriptSegment(speaker=staff, text="Welcome! I'd be happy to help you with that.", start_time=3.0, end_time=6.0),
            TranscriptSegment(speaker=customer, text="What are your rates?", start_time=6.0, end_time=8.0),
            TranscriptSegment(speaker=staff, text="Our standard package starts at $99 per month.", start_time=8.0, end_time=12.0),
        ]
