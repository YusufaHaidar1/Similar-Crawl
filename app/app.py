from flask import Flask, request, render_template, jsonify, session
import pandas as pd
import io
import os
from linkedin_api import Linkedin
import time
from datetime import datetime
import secrets

# Import the LinkedIn scraper class
from linkedin_scraper import LinkedInAlumniScraper

# Determine the absolute path to the app directory
app_dir = os.path.dirname(os.path.abspath(__file__))

# Create templates directory inside the app directory if it doesn't exist
templates_dir = os.path.join(app_dir, 'templates')
if not os.path.exists(templates_dir):
    os.makedirs(templates_dir)

# Create Flask app with the templates directory inside app folder
app = Flask(__name__, template_folder=templates_dir)
app.secret_key = secrets.token_hex(16)  # Required for session management

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    """Endpoint to handle LinkedIn scraping"""
    try:
        print("Scrape request received")

        # Get search parameters
        limit = int(request.form.get('limit', 50))
        print(f"Scrape limit: {limit}")

        # Check if form credentials were provided
        form_email = request.form.get('linkedin_email')
        form_password = request.form.get('linkedin_password')
        
        if form_email and form_password:
            print("Using form credentials")
            email = form_email
            password = form_password
        else:
            print("Using credentials from file")
            from linkedin_scraper import load_credentials
            email, password = load_credentials()
            
            if not email or not password:
                return jsonify({"error": "LinkedIn credentials not found. Please provide credentials in the form or create a credentials file."}), 400

        print(f"Email: {email}, Password: {'*' * len(password)}")

        # Initialize the scraper
        scraper = LinkedInAlumniScraper(email, password)

        # Start scraping with the provided limit
        scraper.scrape_alumni(limit=limit)

        # Get the results as a DataFrame
        df = scraper.results

        return jsonify({
            "success": True,
            "message": f"Successfully scraped {len(df)} LinkedIn profiles",
            "data": df
        })

    except Exception as e:
        # Ensure errors are returned as JSON
        return jsonify({"error": str(e)}), 500

@app.route('/process', methods=['POST'])
def process():
    # Get uploaded file
    file1 = request.files.get('file1')
    
    # Check if threshold was provided, otherwise use default
    threshold = float(request.form.get('threshold', 0.5))
    
    if not file1:
        return jsonify({"error": "Please upload the Excel file"}), 400
    
    # Get LinkedIn data from the session or from a direct upload
    linkedin_data = session.get('linkedin_data')
    
    # If no LinkedIn data in session, check if file was uploaded
    if not linkedin_data:
        file2 = request.files.get('file2')
        if file2 and file2.filename.endswith('.csv'):
            # Read the CSV file
            df2 = pd.read_csv(file2, header=None)
        else:
            return jsonify({"error": "No LinkedIn data available. Please scrape or upload a CSV file."}), 400
    else:
        # Convert session data to DataFrame
        df2 = pd.DataFrame(linkedin_data)
        # Make sure column order matches expected format for jaccard_similarity function
        df2 = df2[['name', 'current_company', 'current_title']]
        
    try:
        # Read the first file (expecting Excel)
        if file1.filename.endswith('.xlsx') or file1.filename.endswith('.xls'):
            df1 = pd.read_excel(file1, header=None)
        else:
            return jsonify({"error": "First file must be an Excel file (.xlsx or .xls)"}), 400
        
        # Process the first dataframe
        if df1.iloc[0, 0] == 'Nama Mahasiswa':
            df1.columns = df1.iloc[0]  # Use the first row as the header
            df1 = df1[1:]  # Remove the first row after setting it as the header
        
        # Make sure 'Nama Mahasiswa' is in the columns
        if 'Nama Mahasiswa' not in df1.columns:
            return jsonify({"error": "Excel file must contain 'Nama Mahasiswa' column"}), 400
            
        nama = df1['Nama Mahasiswa'].tolist()
        namaa = df2[0].tolist()  # LinkedIn names from first column
        
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
    
@app.route('/download', methods=['POST'])
def download():
    # """Endpoint to download processed results as CSV or Excel"""
    try:
        data = request.json
        if not data or 'results' not in data:
            return jsonify({"error": "No data available for download"}), 400
        
        # Create a DataFrame from the results
        df = pd.DataFrame(data['results'])
        
        # Create a bytes buffer for the file
        buffer = io.BytesIO()
        
        # Determine format from request (default to Excel)
        format_type = request.args.get('format', 'excel')
        
        if format_type == 'csv':
            # Save as CSV
            df.to_csv(buffer, index=False)
            mimetype = 'text/csv'
            filename = 'similarity_results.csv'
        else:
            # Save as Excel
            df.to_excel(buffer, index=False)
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename = 'similarity_results.xlsx'
        
        # Seek to the beginning of the buffer
        buffer.seek(0)
        
        # Create response with the file
        from flask import send_file
        return send_file(
            buffer,
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
        
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