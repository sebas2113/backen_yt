from flask import Flask, jsonify, request
from pytube import YouTube, Search

app = Flask(__name__)

# Endpoint para buscar videos en YouTube
@app.route('/search', methods=['GET'])
def search_videos():
    query = request.args.get('query', '')
    if not query:
        return jsonify({"error": "No query provided"}), 400

    search_results = Search(query).results
    video_list = []

    for video in search_results:
        video_data = {
            "title": video.title,
            "url": video.watch_url,
            "thumbnail": video.thumbnail_url,
            "length": video.length,
        }
        video_list.append(video_data)

    return jsonify(video_list)

# Endpoint para obtener las opciones de calidad del video (video y audio)
@app.route('/streams', methods=['GET'])
def get_streams():
    video_url = request.args.get('url', '')
    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        yt = YouTube(video_url)
        streams = yt.streams
        stream_options = []

        # Agregar opciones de video con audio (progressive)
        for stream in streams.filter(progressive=True):  # Video + audio
            stream_options.append({
                "itag": stream.itag,
                "type": "video",
                "quality": stream.resolution,
                "audio_codec": stream.audio_codec if stream.audio_codec else None,
                "video_codec": stream.video_codec,
                "url": stream.url
            })

        # Agregar opciones solo de audio
        for stream in streams.filter(only_audio=True):  # Solo audio
            stream_options.append({
                "itag": stream.itag,
                "type": "audio",
                "quality": stream.abr,  # Bitrate del audio
                "audio_codec": stream.audio_codec,
                "url": stream.url
            })

        return jsonify(stream_options)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint para descargar video o audio según la calidad seleccionada
@app.route('/download', methods=['GET'])
def download_video():
    video_url = request.args.get('url', '')
    itag = request.args.get('itag', '')
    if not video_url or not itag:
        return jsonify({"error": "No URL or ITAG provided"}), 400

    try:
        yt = YouTube(video_url)
        stream = yt.streams.get_by_itag(itag)

        if not stream:
            return jsonify({"error": "Stream with given ITAG not found"}), 404

        # Descarga el video o audio según el ITAG proporcionado
        stream.download()  # Descarga el archivo en el directorio actual
        return jsonify({"message": "Download successful"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)