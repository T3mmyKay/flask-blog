from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import SubmitField


class CreateCommentForm(FlaskForm):
    comment = CKEditorField(label='Comment', validators=[DataRequired()])
    submit = SubmitField(label="Add Comment")
