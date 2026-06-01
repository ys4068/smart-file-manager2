"""应用入口"""
from app import create_app, db
from flask_migrate import Migrate

app = create_app('development')
migrate = Migrate(app, db)

with app.app_context():
    # 仅在开发环境自动建表，生产环境请使用 flask db upgrade
    db.create_all()
    print("✅ 数据库表已创建")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
