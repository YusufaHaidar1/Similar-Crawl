from flask import Flask, request, render_template, jsonify
import pandas as pd
import io
import os

# Determine the absolute path to the app directory
app_dir = os.path.dirname(os.path.abspath(__file__))

# Create templates directory inside the app directory if it doesn't exist
templates_dir = os.path.join(app_dir, 'templates')
if not os.path.exists(templates_dir):
    os.makedirs(templates_dir)

# Create Flask app with the templates directory inside app folder
app = Flask(__name__, template_folder=templates_dir)

# Write the template file
template_path = os.path.join(templates_dir, 'index.html')
with open(template_path, 'w') as f:
    f.write('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jaccard Similarity Tool</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="file"], input[type="number"] {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            display: block;
            margin: 20px auto;
            width: 200px;
        }
        button:hover {
            background-color: #45a049;
        }
        .result-section {
            margin-top: 30px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
            position: sticky;
            top: 0;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        tr:hover {
            background-color: #f1f1f1;
        }
        .loading {
            text-align: center;
            display: none;
        }
        .spinner {
            border: 6px solid #f3f3f3;
            border-top: 6px solid #3498db;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 2s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .error {
            color: #ff0000;
            font-weight: bold;
            text-align: center;
            margin: 15px 0;
        }
        .instructions {
            background-color: #e9f7ef;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .instructions h3 {
            margin-top: 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Jaccard Similarity Tool</h1>
        
        <div class="instructions">
            <h3>Instructions:</h3>
            <p>1. Upload an Excel file containing student names with a column header "Nama Mahasiswa"</p>
            <p>2. Upload a CSV file containing LinkedIn profiles (name in first column, workplace in second, job in third)</p>
            <p>3. Set similarity threshold (0.5 is default)</p>
            <p>4. Click "Run Similarity" to process the files</p>
        </div>
        
        <div class="form-group">
            <label for="file1">Upload Student Excel File (.xlsx):</label>
            <input type="file" id="file1" accept=".xlsx, .xls">
        </div>
        
        <div class="form-group">
            <label for="file2">Upload LinkedIn CSV File (.csv):</label>
            <input type="file" id="file2" accept=".csv">
        </div>
        
        <div class="form-group">
            <label for="threshold">Similarity Threshold (0-1):</label>
            <input type="number" id="threshold" min="0" max="1" step="0.1" value="0.5">
        </div>
        
        <button id="submitBtn">Run Similarity</button>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Processing files, please wait...</p>
        </div>
        
        <div class="error" id="error"></div>
        
        <div class="result-section" id="resultSection" style="display: none;">
            <h2>Results:</h2>
            <div id="tableContainer" style="max-height: 500px; overflow-y: auto;">
                <table id="resultTable">
                    <thead>
                        <tr id="headerRow"></tr>
                    </thead>
                    <tbody id="resultBody"></tbody>
                </table>
            </div>
        </div>
    </div>
    
    <script>
        document.getElementById('submitBtn').addEventListener('click', function() {
            const file1 = document.getElementById('file1').files[0];
            const file2 = document.getElementById('file2').files[0];
            const threshold = document.getElementById('threshold').value;
            const errorDiv = document.getElementById('error');
            const loadingDiv = document.getElementById('loading');
            const resultSection = document.getElementById('resultSection');
            
            // Reset
            errorDiv.textContent = '';
            resultSection.style.display = 'none';
            
            // Validate files
            if (!file1 || !file2) {
                errorDiv.textContent = 'Please upload both files';
                return;
            }
            
            // Show loading
            loadingDiv.style.display = 'block';
            
            // Create form data
            const formData = new FormData();
            formData.append('file1', file1);
            formData.append('file2', file2);
            formData.append('threshold', threshold);
            
            // Send request
            fetch('/process', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                loadingDiv.style.display = 'none';
                
                if (data.error) {
                    errorDiv.textContent = data.error;
                    return;
                }
                
                // Display results
                displayResults(data.results, data.columns);
                resultSection.style.display = 'block';
            })
            .catch(error => {
                loadingDiv.style.display = 'none';
                errorDiv.textContent = 'An error occurred: ' + error.message;
            });
        });
        
        function displayResults(results, columns) {
            const headerRow = document.getElementById('headerRow');
            const resultBody = document.getElementById('resultBody');
            
            // Clear previous results
            headerRow.innerHTML = '';
            resultBody.innerHTML = '';
            
            // Add headers
            columns.forEach(column => {
                const th = document.createElement('th');
                th.textContent = column;
                headerRow.appendChild(th);
            });
            
            // Add data rows
            results.forEach(row => {
                const tr = document.createElement('tr');
                
                columns.forEach(column => {
                    const td = document.createElement('td');
                    td.textContent = row[column] || '';
                    tr.appendChild(td);
                });
                
                resultBody.appendChild(tr);
            });
        }
    </script>
</body>
</html>
        ''')
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    # Get uploaded files
    file1 = request.files['file1']
    file2 = request.files['file2']
    
    # Check if threshold was provided, otherwise use default
    threshold = float(request.form.get('threshold', 0.5))
    
    if not file1 or not file2:
        return jsonify({"error": "Please upload both files"}), 400
        
    try:
        # Read the first file (expecting Excel)
        if file1.filename.endswith('.xlsx') or file1.filename.endswith('.xls'):
            df1 = pd.read_excel(file1, header=None)
        else:
            return jsonify({"error": "First file must be an Excel file (.xlsx or .xls)"}), 400
            
        # Read the second file (expecting CSV)
        if file2.filename.endswith('.csv'):
            df2 = pd.read_csv(file2, header=None)
        else:
            return jsonify({"error": "Second file must be a CSV file (.csv)"}), 400
        
        # Process the first dataframe
        if df1.iloc[0, 0] == 'Nama Mahasiswa':
            df1.columns = df1.iloc[0]  # Use the first row as the header
            df1 = df1[1:]  # Remove the first row after setting it as the header
        
        # Make sure 'Nama Mahasiswa' is in the columns
        if 'Nama Mahasiswa' not in df1.columns:
            return jsonify({"error": "Excel file must contain 'Nama Mahasiswa' column"}), 400
            
        nama = df1['Nama Mahasiswa'].tolist()
        namaa = df2[0].tolist()
        
        # Jaccard similarity calculation
        hasil = jaccard_similarity(nama, namaa, threshold, df2)
        
        # Create result dataframe
        result_df = pd.DataFrame()
        result_df['Nama Mahasiswa'] = nama
        result_df['Nama LinkedIn'] = result_df['Nama Mahasiswa'].map(lambda x: hasil.get(x, ("", "", ""))[0])
        result_df['Pekerjaan'] = result_df['Nama Mahasiswa'].map(lambda x: hasil.get(x, ("", "", ""))[1])
        result_df['Tempat Kerja'] = result_df['Nama Mahasiswa'].map(lambda x: hasil.get(x, ("", "", ""))[2])
        
        # Convert to JSON for the response, handle NaN values
        result_json = result_df.fillna('').to_dict(orient='records')
        
        # Ensure all values are properly converted to strings
        for record in result_json:
            for key, value in record.items():
                if not isinstance(value, str):
                    record[key] = str(value)
        
        return jsonify({
            "results": result_json,
            "columns": result_df.columns.tolist()
        })
        
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

def jaccard_similarity(nama, namaa, threshold, df2):
    hasil = {}
    for nama1 in nama:
        for i, nama2 in enumerate(namaa):
            if pd.isna(nama1) or pd.isna(nama2):
                continue
                
            # Convert to string if they're not already
            nama1_str = str(nama1)
            nama2_str = str(nama2)
            
            set1 = set(nama1_str)
            set2 = set(nama2_str)
            
            intersection = set1.intersection(set2)
            union = set1.union(set2)
            
            if not union:  # Avoid division by zero
                similarity = 0
            else:
                similarity = len(intersection) / len(union)
                
            if similarity > threshold:
                tempat_kerja = ""
                pekerjaan = ""
                
                if len(df2.columns) >= 3:
                    tempat_kerja = str(df2.iloc[i, 1]) if not pd.isna(df2.iloc[i, 1]) else ""
                    pekerjaan = str(df2.iloc[i, 2]) if not pd.isna(df2.iloc[i, 2]) else ""
                    
                hasil[nama1] = (nama2_str, pekerjaan, tempat_kerja)
                break  # Only take the first match above threshold
                
    return hasil

if __name__ == '__main__':
    app.run(debug=True, port=5000)