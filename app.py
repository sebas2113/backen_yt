from flask import Flask, jsonify, request
import yt_dlp

app = Flask(__name__)

# Ruta principal para confirmar que el backend funciona
@app.route('/')
def index():
    return jsonify({"message": "Backend YouTube Downloader funcionando 🚀"}), 200


# Función para obtener formatos de un video de YouTube
def get_video_formats(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'cookiefile': 'cookies.txt'  # Usamos cookies manuales para evitar bloqueos
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            formats = info_dict.get('formats', [])
            audio_formats = [f for f in formats if f.get('acodec')]

            return audio_formats, info_dict.get('title', 'Sin título')
    except Exception as e:
        raise e


# Ruta para buscar videos por nombre
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "No query provided"}), 400

    ydl_opts = {
        'quiet': True,
        'noplaylist': True,
        'cookiefile': 'cookies.txt'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(f"ytsearch5:{query}", download=False)
            videos = result.get('entries', [])
            video_list = [{"id": v['id'], "title": v['title'], "url": f"https://www.youtube.com/watch?v={v['id']}"} for v in videos]
            return jsonify(video_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Ruta para obtener formatos de un video
@app.route('/formats', methods=['POST'])
def formats():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        audio_formats, title = get_video_formats(url)
        formats_list = [{
            "format_note": f.get("format_note"),
            "abr": f.get("abr"),
            "ext": f.get("ext"),
            "url": f.get("url")
        } for f in audio_formats]

        return jsonify({"title": title, "formats": formats_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Ruta para descargar el video/audio
@app.route('/download', methods=['GET'])
def download():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    ydl_opts = {
        'format': 'bestaudio',
        'quiet': False,
        'outtmpl': f'/tmp/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'noplaylist': True,
        'cookiefile': 'cookies.txt'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return jsonify({"message": "Download completed successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# actualizado

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


   