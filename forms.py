import hashlib
import wtforms

class Wrapper(dict):
    def getall(self, name):
        return self.get(name)

class TwistedForm(wtforms.Form):
    def __init__(self, formdata, *args, **kwargs):
        return super(TwistedForm, self).__init__(Wrapper(formdata, *args, **kwargs))

coord_field = wtforms.FloatField(validators=[wtforms.validators.required()])

class Form(TwistedForm):
    image_url = wtforms.StringField(validators=[wtforms.validators.required()])
    
    upper_left_x = coord_field
    upper_left_y = coord_field
 
    upper_right_x = coord_field
    upper_right_y = coord_field
     
    lower_right_x = coord_field
    lower_right_y = coord_field
     
    lower_left_x = coord_field
    lower_left_y = coord_field
    
    def get_hash(self):
        sha = hashlib.sha1()
        for k in sorted(self.data.keys()):
            sha.update(str(self.data[k]))
        return sha.hexdigest()
    