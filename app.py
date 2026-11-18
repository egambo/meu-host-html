import os
import uuid
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Meu HTML Host</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; text-align: center; background: #f4f4f9;}
            .container { max-width: 600px; margin: auto; padding: 30px; background: white; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
            input[type=file] { margin: 20px 0; font-size: 16px; }
            button { padding: 12px 24px; background-color: #5C5CFF; color: white; border: none; cursor: pointer; border-radius: 5px; font-size: 16px; font-weight: bold;}
            button:hover { background-color: #4b4be6; }
            #result { margin-top: 20px; font-size: 18px; word-break: break-all; }
            a { color: #5C5CFF; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>☁️ Hospedagem Rápida de HTML</h2>
            <p>Selecione um arquivo .html para gerar um link público.</p>
            <form id="uploadForm">
                <input type="file" name="file" accept=".html,.htm" required>
                <br>
                <button type="button" onclick="uploadFile()">Gerar Link</button>
            </form>
            <div id="result"></div>
        </div>
        
        <script>
            function uploadFile() {
                var btn = document.querySelector("button");
                btn.innerText = "Enviando...";
                var formData = new FormData(document.getElementById("uploadForm"));
                fetch("/upload", {
                    method: "POST",
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    btn.innerText = "Gerar Link";
                    if(data.url) {
                        document.getElementById("result").innerHTML = "✅ Link Pronto!<br><br><a href=\\""+data.url+"\\" target=\\"_blank\\">"+data.url+"</a>";
                    } else {
                        document.getElementById("result").innerText = "❌ Erro: " + data.error;
                    }
                })
                .catch(error => {
                    btn.innerText = "Gerar Link";
                    console.error("Error:", error);
                });
            }
        </script>
    </body>
    </html>
    '''

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Arquivo invalido"}), 400
    if file and file.filename.endswith((".html", ".htm")):
        file_id = str(uuid.uuid4())[:8]
        new_filename = f"{file_id}_{file.filename}"
        file.save(os.path.join(UPLOAD_FOLDER, new_filename))
        
        host_url = request.host_url
        if "http://" in host_url and not "localhost" in host_url and not "127.0.0.1" in host_url:
            host_url = host_url.replace("http://", "https://")
            
        url = host_url + "view/" + new_filename
        return jsonify({"url": url})
    return jsonify({"error": "Apenas arquivos HTML sao permitidos"}), 400

@app.route("/view/<filename>")
def view_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
