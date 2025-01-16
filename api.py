from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import logging
from pathlib import Path
from plagiarism_detector import PlagiarismDetector, ReportGenerator

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
# Utiliser un chemin absolu pour le dossier uploads
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'html', 'md', 'py', 'java', 'cpp', 'js', 'ts'}

# Créer le dossier uploads s'il n'existe pas
Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/analyze', methods=['POST'])
def analyze_plagiarism():
    try:
        logger.info("Received analysis request")
        
        # Vérifier les fichiers
        if 'file1' not in request.files or 'file2' not in request.files:
            logger.error("Missing files in request")
            return jsonify({'error': 'Deux fichiers sont requis'}), 400
        
        file1 = request.files['file1']
        file2 = request.files['file2']
        
        logger.info(f"File 1: {file1.filename}, File 2: {file2.filename}")
        
        if file1.filename == '' or file2.filename == '':
            logger.error("Invalid filenames")
            return jsonify({'error': 'Noms de fichiers invalides'}), 400
            
        if not (allowed_file(file1.filename) and allowed_file(file2.filename)):
            logger.error("Unsupported file type")
            return jsonify({'error': 'Type de fichier non supporté'}), 400
        
        # Sauvegarder les fichiers
        filename1 = secure_filename(file1.filename)
        filename2 = secure_filename(file2.filename)
        filepath1 = os.path.join(app.config['UPLOAD_FOLDER'], filename1)
        filepath2 = os.path.join(app.config['UPLOAD_FOLDER'], filename2)
        
        file1.save(filepath1)
        file2.save(filepath2)
        
        logger.info(f"Fichiers sauvegardés : {filepath1}, {filepath2}")
        
        # Analyser le plagiat
        detector = PlagiarismDetector()
        results = detector.detect_plagiarism(filepath1, filepath2)
        
        logger.info(f"Résultats de l'analyse : {results}")
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse : {str(e)}")
        return jsonify({'error': 'Une erreur interne est survenue'}), 500

if __name__ == '__main__':
    logger.info(f"Starting Flask server. Upload folder: {UPLOAD_FOLDER}")
    app.run(debug=True, port=5000)