class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///piligrim2.db'
    SECRET_KEY = '5791628bb0b13ce0c676dfde280ba245'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "blog.piligrim@gmail.com"
    MAIL_PASSWORD = "orvzyysqccrvhdwq"
