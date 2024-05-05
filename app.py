from flask import Flask, render_template
from gif_background_remover import gif_bp  # Import the blueprint we created

app = Flask(__name__)

# Register the blueprint with the app
app.register_blueprint(gif_bp, url_prefix='/gif')

@app.route('/')
def index():
    return render_template('index.html')
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
