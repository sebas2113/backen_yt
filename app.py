from flask import Flask, jsonify, request
import yt_dlp

app = Flask(__name__)

# Función para obtener los formatos de un video de YouTube
def get_video_formats(url):
    ydl_opts = {
        'format': 'bestaudio/best',  # Mejor calidad de audio por defecto
        'quiet': True,
        'extractaudio': True,  # Extraer solo el audio
        'audioquality': 0,  # Mejor calidad posible
        'outtmpl': '/tmp/%(id)s.%(ext)s',  # Ruta temporal para el archivo descargado
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        formats = info_dict.get('formats', [])
        audio_formats = [f for f in formats if f.get('acodec')]

        return audio_formats, info_dict['title']

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "No query provided"}), 400

    ydl_opts = {
        'quiet': True,
        'extractaudio': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(f"ytsearch:{query}", download=False)
            videos = result['entries']
            video_list = [{"id": v['id'], "title": v['title'], "url": v['url']} for v in videos]
            return jsonify(video_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/formats', methods=['GET'])
def formats():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        audio_formats, title = get_video_formats(url)
        formats_list = [{"format": f.get("format_note"), "bitrate": f.get("abr"), "url": f.get("url")} for f in audio_formats]
        return jsonify({"title": title, "formats": formats_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download', methods=['GET'])
def download():
    url = request.args.get('url')
    format_url = request.args.get('format_url')
    if not url or not format_url:
        return jsonify({"error": "No URL or format URL provided"}), 400

    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': False,
            'outtmpl': f'/tmp/{url.split("=")[-1]}.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegAudioConvertor',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        return jsonify({"message": "Download completed successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)