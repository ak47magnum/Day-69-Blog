from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField
from wtforms.validators import DataRequired, URL, Email, Length
from flask_ckeditor import CKEditorField
# from wtforms.validators import Email, Length


# WTForm for creating a blog post
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


# TODO: Create a RegisterForm to register new users
class RegistrationForm(FlaskForm):
    # this would be better for email validation 👇
    name = StringField("Name", validators=[DataRequired()])
    email = EmailField(label='Email', validators=[DataRequired(), Email()])
    password = PasswordField(label='Password', validators=[
                             DataRequired(), Length(min=8, max=50)])
    submit = SubmitField(label='Register')

# TODO: Create a LoginForm to login existing users
class LoginForm(FlaskForm):
    # this would be better for email validation 👇
    email = EmailField(label='Email', validators=[DataRequired(), Email()])
    password = PasswordField(label='Password', validators=[
                             DataRequired(), Length(min=3, max=50)])
    submit = SubmitField(label='Login')



# # TODO: Create a CommentForm so users can leave comments below posts  ##########################
# class CommentForm(FlaskForm):
#     # this would be better for email validation 👇
#     Comment = StringField("Name", validators=[DataRequired()])
#     submit = SubmitField(label='submit')



# TODO: Create a CommentForm so users can leave comments below posts
class CommentForm(FlaskForm):
    # this would be better for email validation 👇
    comment = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField(label='submit')