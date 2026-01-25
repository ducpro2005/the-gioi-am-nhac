@app.route('/thesis/<thesisname>')
def serve_thesis_pdf(thesisname):
    filename = f"{os.path.basename(thesisname)}.pdf"
    directory = os.path.join(app.root_path, 'templates')
    return send_from_directory(directory, filename, as_attachment=False)