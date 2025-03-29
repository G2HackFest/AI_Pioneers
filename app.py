from flask import Flask, render_template, request, jsonify
import os
import pandas as pd
import zipfile
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
ALLOWED_EXTENSIONS = {'csv', 'zip', 'json', 'xlsx'}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create folders if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_csv(filepath):
    """Process CSV file and return summary statistics"""
    df = pd.read_csv(filepath)
    return {
        'columns': list(df.columns),
        'summary_stats': df.describe().to_dict(),
        'row_count': len(df)
    }

def process_zip(filepath):
    """Process ZIP file containing data files"""
    results = {}
    with zipfile.ZipFile(filepath, 'r') as zip_ref:
        for file in zip_ref.namelist():
            if file.endswith('.csv'):
                with zip_ref.open(file) as f:
                    df = pd.read_csv(f)
                    results[file] = {
                        'columns': list(df.columns),
                        'row_count': len(df)
                    }
    return results

def process_file(filepath):
    """Route file to appropriate processor based on extension"""
    if filepath.endswith('.csv'):
        return process_csv(filepath)
    elif filepath.endswith('.zip'):
        return process_zip(filepath)
    elif filepath.endswith('.json'):
        with open(filepath) as f:
            data = json.load(f)
        return {'items': len(data)} if isinstance(data, list) else {'keys': list(data.keys())}
    else:
        return {'error': 'Unsupported file type for processing'}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return jsonify({'success': False, 'message': 'No files selected'}), 400
    
    files = request.files.getlist('files')
    if len(files) == 0:
        return jsonify({'success': False, 'message': 'No files selected'}), 400
    
    results = []
    
    for file in files:
        if file.filename == '':
            results.append({
                'filename': 'empty',
                'error': 'No selected file',
                'status': 'failed'
            })
            continue
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            try:
                # Save original file
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Process the file
                processing_result = process_file(filepath)
                
                # Save processed results
                processed_filename = f"processed_{filename.split('.')[0]}.json"
                processed_path = os.path.join(app.config['PROCESSED_FOLDER'], processed_filename)
                with open(processed_path, 'w') as f:
                    json.dump(processing_result, f)
                
                results.append({
                    'filename': filename,
                    'size': os.path.getsize(filepath),
                    'status': 'success',
                    'processing_result': processing_result
                })
            except Exception as e:
                results.append({
                    'filename': filename,
                    'error': str(e),
                    'status': 'failed'
                })
        else:
            results.append({
                'filename': file.filename,
                'error': 'File type not allowed',
                'status': 'failed'
            })
    
    success = all(r['status'] == 'success' for r in results)
    message = f"Processed {len(results)} file(s)" + ("" if success else " with errors")
    
    return jsonify({
        'success': success,
        'message': message,
        'data': {
            'processed_files': results,
            'total_files': len(results),
            'successful': sum(1 for r in results if r['status'] == 'success')
        }
    })

if __name__ == '__main__':
    app.run(debug=True)