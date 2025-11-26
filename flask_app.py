from app import create_app
from app.models import db
import os

app = create_app('ProductionConfig')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


with app.app_context():
    db.create_all()
    
app.run()