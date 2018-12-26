from django.test import TestCase
from django.urls import reverse

from outings.models import Outing
from activities.models import Activity
from profiles.models import CustomUser


# class OutingCreatePageTestCase(TestCase):
#     def setUp(self):
#         '''Run before each test'''
#         self.alpinisme = Activity.objects.create(name="Alpinisme")
#         self.customuser = CustomUser.objects.create_user(email="test@gmail.com", username="test", password="testpassword")

#     def test_new_outing_is_created(self):
#         '''Test that a new outing is created and saved in the database.'''
#         nb_of_old_outings = Outing.objects.count()
#         response = self.client.post(reverse('outings:create'), {
#             'title': 'Meije',
#             'description': 'Traversée de la Meije avec bivouac au Grand Pic.',
#             'start_date': '9/10/2018', # try with format '2006-10-25'
#             'end_date': '10/10/2018',
#             'author': self.customuser,
#             'activities': self.alpinisme
#         })
#         # outing = Outing.objects.create(
#         #     title= 'Meije',
#         #     description= 'Traversée de la Meije avec bivouac au Grand Pic.',
#         #     start_date= date.today(),
#         #     end_date= date.today() + timedelta(days=2),
#         #     author= self.customuser
#         # )
#         # print(outing)
#         nb_of_new_outings = Outing.objects.count()
#         self.assertEqual(nb_of_new_outings, nb_of_old_outings + 1)