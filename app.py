from flask import Flask, render_template
import pandas as pd

app = Flask(__name__, template_folder='templates')

@app.route('/')
@app.route('/csv')  
def download_csv():  
    data = pd.read_csv('bookings.csv', sep=';', encoding='utf-8')

    return render_template(
        'download.html', 
        tables=[data.to_html()], 
        titles=[''],
    )
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,)