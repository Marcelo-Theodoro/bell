# Bell API

## Description



Bell API is a solution for storing information of phone calls and bill reports creation. Built with flexibility, code readability, loose coupling and tight cohesion as principles, it can be easily adapted to different needs with a low cost investment.



## Installing and testing instructions



The project depends on [Python 3.7.4](https://www.python.org/downloads/release/python-374/) and [pipenv](https://github.com/pypa/pipenv), therefore you must have both installed in your machine.



Inside the project directory run the following command start a new environment and install the dependencies:

`$ pipenv install --dev`



After that you'll be able to:

- Start the local server with: `$ ./manage.py runserver`

- Run the tests: `$ manage.py tests`

- Run the tests with the coverage report: `$ coverage run --source='.' manage.py test && coverage report`



In case you are planning to send commits to this project, please, do not forget to install the [pre-commits](https://github.com/pre-commit/pre-commit) hooks with `$ pre-commit install`.




## Development environment



Proudly made using Ubuntu 18.04.2 LTS on my Dell Inspiron 7472.

I'm an Atom user, but in this project I wanted to try the VS code.

The [Black](https://github.com/python/black) formatting helped me save a lot of seconds that otherwise would be wasted manually formatting the code.

[pre-commits](https://github.com/pre-commit/pre-commit) hooks to not make dumb mistakes, like forget the `makemigration` or wrong import sorting.

[restless](https://github.com/toastdriven/restless) to handle the endpoint without standing in my way in other parts of the code, like forms.

[pendulum](https://pendulum.eustace.io/) to handle `datetime` calculations without getting crazy.

[FreezeGun](https://github.com/spulec/freezegun) to allow my tests to travel through time.



## API documentation



API documentation available in the Swagger UI: http://mth-bell.herokuapp.com/static/docs/index.html

In case you prefer the OpenAPI file, you can download it here: http://mth-bell.herokuapp.com/static/docs/v1.yaml




## Project design



### The calls app



In the `calls.views.api_v1` we have two endpoints, one for call start data, another for call end data. The decision to create two endpoints instead of one was just to handle the preparer selection and form manipulation. In case we need to use only one endpoint for both start and end data, it could be easily done by changing only the `urls_v1.py` and `api_v1.py` files. Something like this would be enough:



```python
FORMS = {'start': StartRecordForm, 'end': EndRecordForm}
PREPARERS = {'start': START_RECORD_PREPARER, 'end': END_RECORD_PREPARER}

class RecordResource(BaseResource):

    @property
    def form(self):
        call_type = self.data.get('type')
        return FORMS[call_type]

    @property
    def preparer(self):
        call_type = self.data.get('type')
        return PREPARERS[call_type]
```



All the validations are a responsibility of the `calls.forms`, just as the `Record` creation in the `calls.forms.BaseRecordForm.save` method.



The creation of the `Record` make between two and three queries, as you can see in the table below:



|action            |conditions        | qty of queries |
|------------------|------------------|----------------|
|Create Start Call |No end call       | 2              |
|Create End Call   |No start call     | 2              |
|Create Start Call |End call exists   | 3              |
|Create End Call   |Start call exists | 3              |
| Invalid data     | Any              | 0              |



Timeline of database calls:



- New valid form is instantiated, we check if a `Record` with this `call_id` exists with a SELECT

- it exists: We UPDATE the `Record` and in the `post_save` of the `Record`, we create the `Report` instance. Three queries total

- it does not exist: We INSERT the data to create a New Record. Two queries total



This part of the code was written with more an idea of LBYL (look before you leap) in mind because I do think that this kind of code is simpler and the code is more readable.

If performance demonstrate to be an important factor, we could change the mindset to something more alike EAFP (it’s easier to ask for forgiveness than permission).

There are a lot of details that would have to be worked out to use EAFP, like the uniquess validation and ORM default behavior, but the basic idea is:



- We can't assume any order in the information, but we can assume that sometimes (not enough info to know how much) the start call detail will be sent sooner than the end call detail. This is will be our "Happy Path": Have the start before the end.



Based on our Happy Path, when we have a call to create a start record detail, instead of checking if there is an end call detail for this `call_id`, we will just try to INSERT the data in the database. If we really don't have a `Record` with this `call_id`, the instance will be saved without problems, using only one query.

If the end call detail with this `call_id` already exists, we handle that in an `exception` block and update it. As this is not our Happy Path, we'll use three queries.



The same thing for the end record detail, but instead of trying to INSERT, first we'll try to UPDATE.

If the UPDATE is successful, we'll have used only two queries: One to UPDATE and another one to create the `Report` row.

In case it fails, we INSERT the data. Using two queries: One of the UPDATE that failed, another of the INSERT.



As an example:



```python
class  StartRecordForm(BaseRecordForm):

(....)

def save(self, *args, **kwargs):
try:
    Record.objects.create(**self.prepared_data)
except IntegrityError: # Exception raised because of the uniquess of the Record.call_id
    data = copy(self.prepared_data)
    Record.objects.filter(call_id=data.pop('call_id')).update(**data)


class  EndRecordForm(BaseRecordForm):

(....)

def save(self, *args, **kwargs):
    data = copy(self.prepared_data)
    updated = Record.objects.filter(call_id=data.pop('call_id')).update(**data)
    if not updated:
        # none records updated
        data = copy(self.prepared_data)
        Record.objects.create(**data)

```



There are a lot more details, but this is the idea.




About the `calls.models.Record`, I chose to use just one Model and one instance to represent a Call because a feel like the call start detail or call end detail alone are not enough to represent an useful information. We need these two parts to have something that is worthy.

This has a big disadvantage, that is not being able to use the validation of missing values from the ORM/database. In this case I think this is OK since we are doing all the required validations in the Form.



### The reports app



In the `reports.api_v1` we have a simple view that is capable of validate the format of the `period` if passed, or get the last closed period if not, and filter the Reports from this period. I didn't add pagination in this case, but could be easily done if needed.

Based on my understood of what was required in the tests, I worked with the idea that the `period` would come in the format `MM/YYYY`. I'd prefer to use separated query string for that, like `?year=2017&month=02`.



The core of the price calculation is in the `reports.models.Report.minutes_in_each_tarrif` method. In this method, we iterate over the days to get the points in time where we should start and stop charging the standard fee.
I validated the price of the calls based on my manual calculations to be sure if the values returned from the API are correct. In a real world project, I'd ask for more developers and PO's to review my calculations avoiding any kind of bias, but in the case of this test, I had no one to ask, which makes me unease about the correctness of the information.



### Final comments

I don't remember the last time I started a project from scratch. I had to re-learn some details about starting a project.

I'm not used to work alone, I've been working in teams since I started to program, so I missed someone to discuss possible solutions with me and tell me if I'm not crazy about something. But anyway, it was fun to work on this project.

Hope to discuss with you about this in a near future!

Thanks for the opportunity.
