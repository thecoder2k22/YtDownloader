from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/')
def home():
    return 'Welcome to the YouTube Formats Fetcher API!'

@app.route('/get_formats', methods=['GET'])
def get_available_formats():
    try:
        # Get the URL from the request
        url = request.args.get('url')

        if not url:
            return jsonify({'error': 'No URL provided'}), 400

        # yt-dlp options for fetching available formats
        ydl_opts = {
            'quiet': False,  # Suppress output
            'skip_download': True,  # Do not download, only fetch metadata
        }

        # Use yt-dlp to extract information and available formats
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)

            # Extract the cookies used by yt-dlp
            cookies = ""
            if ydl.cookiejar:
                cookies_list = []
                for cookie in ydl.cookiejar:
                    cookie_pair = f"{cookie.name}={cookie.value}; Domain={cookie.domain}; Path={cookie.path};"
                    if cookie.expires:
                        cookie_pair += f" Expires={cookie.expires};"
                    if cookie.secure:
                        cookie_pair += " Secure;"
                    cookies_list.append(cookie_pair)
                cookies = " ".join(cookies_list)

            # Get all available formats
            formats = info_dict.get('formats', [])

            # Collect format details
            available_formats = []
            for f in formats:
                format_info = {
                    'format_id': f.get('format_id'),
                    'ext': f.get('ext'),  # File extension (e.g., mp4, webm)
                    'resolution': f.get('resolution') or f.get('height'),  # Video resolution (e.g., 1080p)
                    'fps': f.get('fps'),  # Frame rate
                    'vcodec': f.get('vcodec'),  # Video codec (e.g., avc1)
                    'acodec': f.get('acodec'),  # Audio codec (e.g., mp4a)
                    'filesize': f.get('filesize') or f.get('filesize_approx'),  # File size (bytes)
                    'url': f.get('url'),  # Direct download URL
                }
                available_formats.append(format_info)

            # Get the thumbnail URL
            thumbnail = info_dict.get('thumbnail')

        # Return the available formats, cookies, and thumbnail as JSON response
        return jsonify({
            'title': info_dict.get('title'),
            'uploader': info_dict.get('uploader'),
            'thumbnail': thumbnail,
            'available_formats': available_formats,
            'cookies': cookies
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run()
