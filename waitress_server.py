from waitress import serve
import app
serve(app.app, host='0.0.0.0', port=8080,threads=8)
