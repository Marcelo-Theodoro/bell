from restless.dj import DjangoResource
from restless.exceptions import BadRequest


class BaseResource(DjangoResource):
    def is_authenticated(self):
        return True

    def create(self):
        form = self.form(self.data)
        if form.is_valid():
            call = form.save()
            return call
        raise BadRequest(form.errors)
