from django.test import TestCase
from django.urls import reverse

from profiles.models import CustomUser, Profile
from activities.models import Activity


class HomepageTestCase(TestCase):
    '''Test that 'homepage' returns a 200'''
    def test_homepage_200(self):
        response = self.client.get(reverse('homepage'))
        self.assertEqual(response.status_code, 200)

class ProfileDetailPageTestCase(TestCase):
    def setUp(self):
        '''Run before each test'''
        alpinisme = Activity.objects.create(name="Alpinisme")
        ski = Activity.objects.create(name="Ski")
        customuser = CustomUser.objects.create_user(email="test@gmail.com", username="test", password="testpassword")
        self.profile = Profile.objects.create(user=customuser, availability_area="Alpes")
        self.profile.activities.add(ski, alpinisme)

    def test_profile_detail_page_200(self):
        '''Test that 'profiles:detail' returns a 200 if the item exists'''
        response = self.client.get(reverse('profiles:detail', kwargs={'username': self.profile.user.username}))
        self.assertEqual(response.status_code, 200)

    def test_profile_detail_page_404(self):
        '''Test that 'profiles:detail' returns a 404 if the item does not exist'''
        tintin = CustomUser.objects.create_user(email="tintin@gmail.com", username="tintin", password="tintinpassword")
        self.profile.user = tintin
        response = self.client.get(reverse('profiles:detail', kwargs={'username': self.profile.user.username}))
        self.assertEqual(response.status_code, 404)


'''
from profiles.models import Profile
from activities.models import Activity, Grade

Profile.objects.get(user__email='dernier@gmail.com').activities.all()
activities = self.instance.activities.all()
Grade.objects.select_related('activity').filter(eval(' | '.join(f'Q(activity="{ activity.pk }")' for activity in activities)))

'''



'''
ProfileFormTestCase

from profiles.models import CustomUser, Profile
from activities.models import Activity, Grade

alpinisme = Activity.objects.create(name="Alpinisme")
ski = Activity.objects.create(name="Ski")
alpinismed = Grade.objects.create(activity=alpinisme, name='D', ordering=1)
alpinismetd = Grade.objects.create(activity=alpinisme, name='TD', ordering=2)
alpinismeed = Grade.objects.create(activity=alpinisme, name='ED', ordering=3)
skiquatre = Grade.objects.create(activity=ski, name='4', ordering=1)
skicinq = Grade.objects.create(activity=ski, name='5', ordering=2)


loggedinuser = CustomUser.objects.create_user(email="loggedin@gmail.com", username="loggedin", password="loginpwd", is_profile="True")
loggedinprofile = Profile.objects.create(user=loggedinuser, availability_area="Alpes")
loggedinprofile.activities.add(ski, alpinisme)
loggedinprofile.grades.add(alpinismed, alpinismetd, skiquatre)

print(loggedinprofile.activities)
print(Profile.objects.get(user__username=loggedin))

''' 