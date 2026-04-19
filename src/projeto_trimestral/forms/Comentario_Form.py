from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class Comentario_Form(FlaskForm):
    texto = StringField('Comentário: ', validators=[DataRequired()])
    submit = SubmitField('Comentar', validators=[DataRequired()])