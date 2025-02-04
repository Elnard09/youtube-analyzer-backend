from flask import Flask, request, jsonify, send_file
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline
from docx import Document
import pdfkit
import os

app = Flask(__name__)

# Initialize summarization pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

pdfkit_config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')  # Update path if neededpython app.py

@app.route('/extract-transcript', methods=['GET'])
def extract_transcript():
    video_url = request.args.get('video_url')
    if not video_url:
        return jsonify({'error': 'Missing video_url parameter'}), 400
    
    try:
        video_id = video_url.split('v=')[1].split('&')[0]  # Extract video ID from URL
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = ' '.join([t['text'] for t in transcript])
        return jsonify({'transcript': transcript_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/summarize-video', methods=['GET'])
def summarize_video():
    video_url = request.args.get('video_url')
    if not video_url:
        return jsonify({'error': 'Missing video_url parameter'}), 400
    
    try:
        video_id = video_url.split('v=')[1].split('&')[0]
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = ' '.join([t['text'] for t in transcript])
        
        # Summarize the transcript
        summary = summarizer(transcript_text, max_length=150, min_length=30, do_sample=False)
        return jsonify({'summary': summary[0]['summary_text']})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/generate-downloadable-file', methods=['GET'])
def generate_downloadable_file():
    content = request.args.get('content')
    file_format = request.args.get('file_format')
    
    if not content or not file_format:
        return jsonify({'error': 'Missing content or file_format parameter'}), 400
    
    try:
        if file_format == 'docx':
            doc = Document()
            doc.add_paragraph(content)
            doc.save('output.docx')
            return send_file('output.docx', as_attachment=True)
        
        elif file_format == 'pdf':
            pdfkit.from_string(content, 'output.pdf')
            return send_file('output.pdf', as_attachment=True)
        
        elif file_format == 'txt':
            with open('output.txt', 'w') as f:
                f.write(content)
            return send_file('output.txt', as_attachment=True)
        
        else:
            return jsonify({'error': 'Invalid file format'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)