from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class Post_Form(FlaskForm):
    escola = StringField('Escola: ', validators=[DataRequired()])
    titulo = StringField('Título: ', validators=[DataRequired()])
    texto = StringField('Texto da publicação: ', validators=[DataRequired()])

    submit = SubmitField('Publicar Post')