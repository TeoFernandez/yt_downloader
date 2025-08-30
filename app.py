from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import uuid  # Para nombres de archivos únicos

app = Flask(__name__)

# Carpeta para archivos temporales
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        download_type = request.form['type']  # 'video' o 'audio'

        # Opciones para yt-dlp
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }

        if download_type == 'audio':
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
            ext = 'mp3'
        else:
            ydl_opts['format'] = 'bestvideo+bestaudio/best'
            ext = 'mp4'

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                # Obtener el nombre del archivo descargado
                filename = ydl.prepare_filename(info)
                if download_type == 'audio':
                    filename = filename.replace('.webm', '.mp3')  # Ajuste para audio
                    filename = filename.replace('.m4a', '.mp3')

            # Renombrar a algo único para evitar conflictos
            unique_filename = f"{uuid.uuid4()}.{ext}"
            unique_path = os.path.join(DOWNLOAD_FOLDER, unique_filename)
            os.rename(filename, unique_path)

            # Enviar el archivo al usuario
            return send_file(unique_path, as_attachment=True, download_name=info['title'] + f'.{ext}')

        except Exception as e:
            return f"Error: {str(e)}"

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)