from wtforms import Form, StringField, PasswordField, DateField, TimeField, validators, BooleanField

class SignupForm(Form):
    username = StringField('Kullanıcı Adı', [validators.Length(min=4, max=25)])
    password = PasswordField('Şifre', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Şifreler eşleşmelidir')
    ])
    confirm = PasswordField('Şifreyi Tekrarla')
    email = StringField('E-posta', [validators.Length(min=6, max=35)])
    birth_date = DateField('Doğum Tarihi', format='%Y-%m-%d')
    birth_time = TimeField('Doğum Saati', format='%H:%M')
    city = StringField('Doğum Yeri', [validators.Length(min=2, max=35)])

class SigninForm(Form):
    username = StringField('Kullanıcı Adı', [validators.Length(min=4, max=25)])
    password = PasswordField('Şifre', [validators.DataRequired()])
    remember = BooleanField('Beni Hatırla') 