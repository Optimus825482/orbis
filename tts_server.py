from flask import Flask, request, jsonify
import edge_tts
import asyncio
import io
import base64
import logging
import os
import tempfile


def create_tts_app():
    app = Flask(__name__)

    @app.route("/api/tts", methods=["POST"])
    async def text_to_speech():
        try:
            data = request.json
            text = data.get("text")
            action = data.get("action", "play")
            rate = data.get("rate", "+40%")  # Konuşma hızı parametresi eklendi

            if not text:
                return jsonify({"error": "Metin boş olamaz"}), 400

            # Edge TTS için Türkçe kadın sesi
            voice = "tr-TR-EmelNeural"

            communicate = edge_tts.Communicate(
                text, voice, rate=rate
            )  # rate parametresi eklendi

            # Geçici dosya oluştur
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, f"temp_speech_{os.getpid()}.mp3")

            try:
                # Sesi dosyaya kaydet
                await communicate.save(temp_path)

                # MP3 dosyasını oku ve base64'e çevir
                with open(temp_path, "rb") as f:
                    audio_data = f.read()
                audio_base64 = base64.b64encode(audio_data).decode()

                return jsonify(
                    {"audio": audio_base64, "format": "audio/mp3", "status": "success"}
                )

            finally:
                # Geçici dosyayı sil
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                except:
                    pass

        except Exception as e:
            logging.error(f"TTS hatası: {str(e)}")
            return jsonify({"error": str(e)}), 500

    return app


if __name__ == "__main__":
    app = create_tts_app()
    app.run(port=5003)
