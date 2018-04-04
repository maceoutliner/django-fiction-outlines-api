import logging
import pytest
from django.core.exceptions import ObjectDoesNotExist
from test_plus import APITestCase
from fiction_outlines.models import Series, Character, Location, Outline, Arc
from fiction_outlines.models import StoryElementNode, ArcElementNode
from fiction_outlines.models import CharacterInstance, LocationInstance
from fiction_outlines_api.serializers import SeriesSerializer, CharacterSerializer, LocationSerializer
from fiction_outlines_api.serializers import OutlineSerializer, ArcSerializer, CharacterInstanceSerializer
from fiction_outlines_api.serializers import LocationInstanceSerializer, ArcElementNodeSerializer
from fiction_outlines_api.serializers import StoryElementNodeSerializer

logger = logging.getLogger('test_apiviews')
logger.setLevel(logging.DEBUG)


class FictionOutlineAbstractTestCase(APITestCase):
    '''
    An abstract class to make test setup less repetitive.
    '''

    def setUp(self):
        '''
        Generic data setup for test cases.
        '''
        logger.debug('Setting up...')
        self.extra = {'format': 'json'}
        self.user1 = self.make_user('u1')
        self.user2 = self.make_user('u2')
        self.user3 = self.make_user('u3')
        self.naughty_users = [self.user2, self.user3]
        self.s1 = Series(title='Urban Fantasy Series', user=self.user1)
        self.s1.save()
        self.s2 = Series(title='Space Opera Trilogy', user=self.user1)
        self.s2.save()
        self.s3 = Series(title='Mil-SF series', user=self.user2)
        self.s3.save()
        self.c1 = Character(name='John Doe', user=self.user1)
        self.c2 = Character(name='Jane Doe', user=self.user1)
        self.c1.save()
        self.c1.tags.add('ptsd', 'anxiety')
        self.c2.save()
        self.c2.tags.add('teen', 'magical')
        self.c1.series.add(self.s1)
        self.c2.series.add(self.s2)
        self.c3 = Character(name='Michael Smith', user=self.user2)
        self.c4 = Character(name='Eliza Doolittle', user=self.user2)
        self.c3.save()
        self.c3.series.add(self.s3)
        self.c4.save()
        self.c4.tags.add('murderess')
        self.o1 = Outline(title='OOGA', user=self.user1)
        self.o2 = Outline(title='Chicken Little', user=self.user1)
        self.o3 = Outline(title='Dancing Rabbit', user=self.user2)
        self.o1.save()
        self.o2.save()
        self.o3.save()
        self.c1int = CharacterInstance(outline=self.o1, character=self.c1)
        self.c2int = CharacterInstance(outline=self.o1, character=self.c2)
        self.c1int2 = CharacterInstance(outline=self.o2, character=self.c1)
        self.c3int = CharacterInstance(outline=self.o3, character=self.c3)
        self.c1int.save()
        self.c2int.save()
        self.c1int2.save()
        self.c3int.save()
        self.l1 = Location(name='Abandoned Warehouse', user=self.user1)
        self.l1.save()
        self.l1.series.add(self.s1)
        self.l1int = LocationInstance(outline=self.o1, location=self.l1)
        self.l1int.save()
        self.l2 = Location(name='Ghost Ship', user=self.user1)
        self.l2.save()
        self.l2.series.add(self.s2)
        self.l2int = LocationInstance(outline=self.o1, location=self.l2)
        self.l2int.save()
        self.l1int2 = LocationInstance(outline=self.o2, location=self.l1)
        self.l1int2.save()
        self.l3 = Location(name='Haunted house', user=self.user2)
        self.l3.save()
        self.l3.series.add(self.s2)
        self.l3int = LocationInstance(outline=self.o1, location=self.l3)
        self.l3int.save()
        self.l4 = Location(name='The damn bar', tags='humor', user=self.user2)
        self.l4.save()
        self.l4int = LocationInstance(outline=self.o3, location=self.l4)
        self.l4int.save()
        self.arc1 = self.o1.create_arc(name='Coming of age', mace_type='character')
        self.arc2 = self.o1.create_arc(name='dragon invastion', mace_type='event')
        self.arc3 = self.o2.create_arc(name='AIs turn against us', mace_type='event')
        self.arc4 = self.o2.create_arc(name='Overcome alien predjudice', mace_type='character')
        self.arc5 = self.o3.create_arc(name='Travel to fairie and get back', mace_type='milieu')


class SeriesListTestCase(FictionOutlineAbstractTestCase):
    '''
    Test case for series listing.
    '''

    def test_login_required(self):
        '''
        You have to be logged in.
        '''
        self.get('fiction_outlines_api:series_listcreate')
        self.response_403()

    def test_authenticated_user(self):
        '''
        Ensure that users cannot see series that another owns.
        '''
        forbidden_series = SeriesSerializer(Series.objects.filter(user=self.user1), many=True)
        for user in self.naughty_users:
            with self.login(username=user.username):
                self.assertGoodView('fiction_outlines_api:series_listcreate')
                results = self.last_response.data
                for fs in forbidden_series.data:
                    assert fs not in results
        with self.login(username=self.user1.username):
            self.assertGoodView('fiction_outlines_api:series_listcreate')
            results = self.last_response.data
            for fs in forbidden_series.data:
                assert fs in results


class SeriesCreateTestCase(FictionOutlineAbstractTestCase):
    '''
    Test for API creation of series.
    '''

    data = {
        'title': 'Monkeys of heaven',
        'description': 'The second trilogy in my astral primates cycle.',
        'tags': ['primates', 'astral'],
    }
    extra = {'format': 'json'}

    def test_login_required(self):
        '''
        you have to be logged in.
        '''
        self.post('fiction_outlines_api:series_listcreate', data=self.data, extra=self.extra)
        self.response_403()

    def test_authenticated_user(self):
        before_create = Series.objects.filter(user=self.user1).count()
        with self.login(username=self.user1.username):
            self.post('fiction_outlines_api:series_listcreate', data=self.data, extra=self.extra)
            print(self.last_response.content)
            self.response_201()
            assert Series.objects.filter(user=self.user1).count() - before_create == 1
            latest = Series.objects.latest('created')
            assert 'Monkeys of heaven' == latest.title
            assert latest.tags.count() == 2


class SeriesDetailTestCase(FictionOutlineAbstractTestCase):
    '''
    Tests for viewing series details.
    '''
    extra = {'format': 'json'}

    def test_login_required(self):
        '''
        You have to be logged in.
        '''
        self.get('fiction_outlines_api:series_item', series=self.s1.pk, extra=self.extra)
        self.response_403()

    def test_object_permissions(self):
        '''
        Ensure an unauthorized user cannot access the items.
        '''
        for user in self.naughty_users:
            with self.login(username=user.username):
                print("Valid url should be: api/v1/series/%s/" % self.s1.pk)
                self.get('fiction_outlines_api:series_item', series=self.s1.pk, extra=self.extra)
                self.response_403()

    def test_authorized_user(self):
        '''
        Verify that authorized user can access the item.
        '''
        with self.login(username=self.user1.username):
            self.assertGoodView('fiction_outlines_api:series_item', series=self.s1.pk, extra=self.extra)
            serialized_object = SeriesSerializer(self.s1)
            assert serialized_object.data == self.last_response.data


class SeriesUpdateView(FictionOutlineAbstractTestCase):
    '''
    Tests for series update functions, both PUT and PATCH.
    '''
    short_data = {'title': 'war of cats'}
    long_data = {
        'title': 'reign of dogs',
        'description': "I'm just going through a lot of stuff right now.",
        'tags': ['dog', 'cry for help'],
    }

    def test_login_required(self):
        '''
        You have to be logged in.
        '''
        self.put('fiction_outlines_api:series_item', series=self.s1.pk, data=self.long_data, extra=self.extra)
        self.response_403()
        assert self.s1.title == Series.objects.get(pk=self.s1.pk).title
        self.patch('fiction_outlines_api:series_item', series=self.s1.pk, data=self.short_data, extra=self.extra)
        self.response_403()
        assert self.s1.title == Series.objects.get(pk=self.s1.pk).title

    def test_object_permissions(self):
        '''
        Ensure that an unauthorized user cannot edit the object.
        '''
        for user in [self.user2, self.user2]:
            with self.login(username=user.username):
                self.put('fiction_outlines_api:series_item', series=self.s1.pk, data=self.long_data, extra=self.extra)
                self.response_403()
                assert self.s1.title == Series.objects.get(pk=self.s1.pk).title
                self.patch('fiction_outlines_api:series_item', series=self.s1.pk,
                           data=self.short_data, extra=self.extra)
                self.response_403()
                assert self.s1.title == Series.objects.get(pk=self.s1.pk).title

    def test_authorized_user(self):
        '''
        Ensure that an authorized user can make the necessary edits.
        '''
        with self.login(username=self.user1.username):
            self.patch('fiction_outlines_api:series_item', series=self.s1.pk, data=self.short_data, extra=self.extra)
            self.response_200()
            patched_s1 = Series.objects.get(pk=self.s1.pk)
            assert patched_s1.title == 'war of cats'
            assert not patched_s1.description
            assert not patched_s1.tags.count()
            self.put('fiction_outlines_api:series_item', series=self.s1.pk, data=self.long_data, extra=self.extra)
            self.response_200()
            put_s1 = Series.objects.get(pk=self.s1.pk)
            assert put_s1.title == 'reign of dogs'
            assert put_s1.description
            assert put_s1.tags.count() == 2


class SeriesDeleteTest(FictionOutlineAbstractTestCase):
    '''
    Test series deletion.
    '''

    def test_login_required(self):
        '''
        You have to be logged in.
        '''
        self.delete('fiction_outlines_api:series_item', series=self.s1.pk, extra=self.extra)
        self.response_403()
        assert Series.objects.get(pk=self.s1.pk)

    def test_unauthorized_users(self):
        '''
        Ensure unauthorized users cannot delete the object.
        '''
        for user in self.naughty_users:
            with self.login(username=user.username):
                self.delete('fiction_outlines_api:series_item', series=self.s1.pk, extra=self.extra)
                self.response_403()
                assert Series.objects.get(pk=self.s1.pk)

    def test_authorized_user(self):
        '''
        Test that an authroized user can delete as expected.
        '''
        with self.login(username=self.user1.username):
            self.delete('fiction_outlines_api:series_item', series=self.s1.pk, extra=self.extra)
            self.response_204()
            with pytest.raises(ObjectDoesNotExist):
                Series.objects.get(pk=self.s1.pk)


# Character Object tests


class CharacterListTestCase(FictionOutlineAbstractTestCase):
    '''
    Test case for character listing.
    '''

    def test_login_required(self):
        '''
        You have to be logged in.
        '''
        self.get('fiction_outlines_api:character_listcreate')
        self.response_403()

    def test_authenticated_user(self):
        '''
        Ensure that users cannot see character that another owns.
        '''
        forbidden_character = CharacterSerializer(Character.objects.filter(user=self.user1), many=True)
        for user in self.naughty_users:
            with self.login(username=user.username):
                self.assertGoodView('fiction_outlines_api:character_listcreate')
                results = self.last_response.data
                for fs in forbidden_character.data:
                    assert fs not in results
        with self.login(username=self.user1.username):
            self.assertGoodView('fiction_outlines_api:character_listcreate')
            results = self.last_response.data
            for fs in forbidden_character.data:
                assert fs in results


class CharacterCreateTestCase(FictionOutlineAbstractTestCase):
    '''
    Test for API creation of characters.
    '''

    data = {
        'name': 'Mary Sue',
        'description': 'She is awesome at everything she does.',
        'tags': ['badass', 'not lame'],
        'series': []
    }

    def setUp(self):
        super().setUp()
        self.data['series'] = [self.s1.pk]

    def test_login_required(self):
        '''
        you have to be logged in.
        '''
        self.post('fiction_outlines_api:character_listcreate', data=self.data, extra=self.extra)
        self.response_403()

    def test_invalid_series(self):
        '''
        Verify that an invalid series is rejected.
        '''
        before_create = Character.objects.filter(user=self.user1).count()
        with self.login(username=self.user1.username):
            self.data['series'].append(self.s3.pk)
            self.post('fiction_outlines_api:character_listcreate', data=self.data, extra=self.extra)
            self.response_403()
            assert before_create == Character.objects.filter(user=self.user1).count()

    def test_authenticated_user(self):
        before_create = Character.objects.filter(user=self.user1).count()
        with self.login(username=self.user1.username):
            self.post('fiction_outlines_api:character_listcreate', data=self.data, extra=self.extra)
            print(self.last_response.content)
            self.response_201()
            assert Character.objects.filter(user=self.user1).count() - before_create == 1
            latest = Character.objects.latest('created')
            assert 'Mary Sue' == latest.name
            assert latest.tags.count() == 2
            data2 = {
                'name': 'Just a guy',
                'description': "You know?",
                'tags': [],
                'series': []
            }
            self.post('fiction_outlines_api:character_listcreate', data=data2, extra=self.extra)
            self.response_201()
            assert Character.objects.filter(user=self.user1).count() - before_create == 2
            latest = Character.objects.latest('created')
            assert latest.name == 'Just a guy'
            assert not latest.tags.count()
            assert not latest.series.count()


class CharacterDetailTestCase(FictionOutlineAbstractTestCase):
    '''
    Tests for viewing character details.
    '''

    def test_login_required(self):
        '''
        You have to be logged in.
        '''
        self.get('fiction_outlines_api:character_item', character=self.c1.pk, extra=self.extra)
        self.response_403()

    def test_object_permissions(self):
        '''
        Ensure an unauthorized user cannot access the items.
        '''
        for user in self.naughty_users:
            with self.login(username=user.username):
                self.get('fiction_outlines_api:character_item', character=self.c1.pk, extra=self.extra)
                self.response_403()

    def test_authorized_user(self):
        '''
        Verify that authorized user can access the item.
        '''
        with self.login(username=self.user1.username):
            self.assertGoodView('fiction_outlines_api:character_item', character=self.c1.pk, extra=self.extra)
            serialized_object = CharacterSerializer(self.c1)
            assert serialized_object.data == self.last_response.data
            assert (len(self.last_response.data['character_instances']) ==
                    CharacterInstance.objects.filter(character=self.c1).count())


class CharacterUpdateView(FictionOutlineAbstractTestCase):
    '''
    Tests for character update functions, both PUT and PATCH.
    '''
    short_data = {'name': 'Inigo Montoya'}
    long_data = {
        'name': 'Doctor Nick',
        'description': "Hi, everybody!",
        'tags': ['discount', 'medical'],
        'series': []
    }

    def setUp(self):
        super().setUp()
        self.long_data['series'] = [self.s1.pk]

    def test_login_required(self):
        '''
        You have to be logged in.
        '''
        self.put('fiction_outlines_api:character_item', character=self.c1.pk, data=self.long_data, extra=self.extra)
        self.response_403()
        assert self.c1.name == Character.objects.get(pk=self.c1.pk).name
        self.patch('fiction_outlines_api:character_item', character=self.c1.pk, data=self.short_data, extra=self.extra)
        self.response_403()
        assert self.c1.name == Character.objects.get(pk=self.c1.pk).name

    def test_object_permissions(self):
        '''
        Ensure that an unauthorized user cannot edit the object.
        '''
        for user in [self.user2, self.user2]:
            with self.login(username=user.username):
                self.put('fiction_outlines_api:character_item', character=self.c1.pk,
                         data=self.long_data, extra=self.extra)
                self.response_403()
                assert self.c1.name == Character.objects.get(pk=self.c1.pk).name
                self.patch('fiction_outlines_api:character_item', character=self.c1.pk,
                           data=self.short_data, extra=self.extra)
                self.response_403()
                assert self.c1.name == Character.objects.get(pk=self.c1.pk).name

    def test_invalid_series(self):
        '''
        Prevent a user from associating a character with a series for which they
        don't have editing rights.
        '''
        with self.login(username=self.user1.username):
            print("s1 = %s" % self.s1.pk)
            print(self.long_data['series'])
            self.long_data['series'].append(self.s3.pk)
            print(self.long_data['series'])
            self.put('fiction_outlines_api:character_item', character=self.c1.pk,
                     data=self.long_data, extra=self.extra)
            print(self.last_response.content)
            self.response_403()
            assert self.c1.series.count() == Character.objects.get(pk=self.c1.pk).series.count()
            self.patch('fiction_outlines_api:character_item', character=self.c1.pk,
                       data={'series': [self.s3.pk, ]}, extra=self.extra)
            self.response_403()
            assert self.c1.series.all()[0] == Character.objects.get(pk=self.c1.pk).series.all()[0]

    def test_authorized_user(self):
        '''
        Ensure that an authorized user can make the necessary edits.
        '''
        with self.login(username=self.user1.username):
            self.patch('fiction_outlines_api:character_item', character=self.c1.pk,
                       data=self.short_data, extra=self.extra)
            self.response_200()
            patched_c1 = Character.objects.get(pk=self.c1.pk)
            assert patched_c1.name == 'Inigo Montoya'
            assert not patched_c1.description
            self.put('fiction_outlines_api:character_item', character=self.c1.pk,
                     data=self.long_data, extra=self.extra)
            self.response_200()
            put_c1 = Character.objects.get(pk=self.c1.pk)
            assert put_c1.name == 'Doctor Nick'
            assert put_c1.description
            assert put_c1.tags.count() == 2
            self.patch('fiction_outlines_api:character_item', character=self.c1.pk,
                       data={'series': []}, extra=self.extra)
            self.response_200()
            series_remove = Character.objects.get(pk=self.c1.pk)
            assert not series_remove.series.count()


class CharacterDeleteTest(FictionOutlineAbstractTestCase):
    '''
    Test character deletion.
    '''

    def test_login_required(self):
        '''
        You have to be logged in.
        '''
        self.delete('fiction_outlines_api:character_item', character=self.c1.pk, extra=self.extra)
        self.response_403()
        assert Character.objects.get(pk=self.c1.pk)

    def test_unauthorized_users(self):
        '''
        Ensure unauthorized users cannot delete the object.
        '''
        for user in self.naughty_users:
            with self.login(username=user.username):
                self.delete('fiction_outlines_api:character_item', character=self.c1.pk, extra=self.extra)
                self.response_403()
                assert Character.objects.get(pk=self.c1.pk)

    def test_authorized_user(self):
        '''
        Test that an authroized user can delete as expected.
        '''
        with self.login(username=self.user1.username):
            self.delete('fiction_outlines_api:character_item', character=self.c1.pk, extra=self.extra)
            self.response_204()
            with pytest.raises(ObjectDoesNotExist):
                Character.objects.get(pk=self.c1.pk)


# CharacterInstance tests


class CharacterInstanceCreateTest(FictionOutlineAbstractTestCase):
    '''
    Test case for creating character instances.
    '''

    def setUp(self):
        super().setUp()
        self.data = {
            'main_character': True,
            'pov_character': True,
            'protagonist': True,
            'antagonist': False,
            'obstacle': False,
            'villain': False
        }
        self.o4 = Outline(title="Test valid outline", description='Hi there.', user=self.user1)
        self.o4.save()

    def test_login_required(self):
        '''
        You have to be logged in.
        '''
        before_create = CharacterInstance.objects.filter(character=self.c1).count()
        self.post('fiction_outlines_api:character_instance_create', character=self.c1.pk,
                  outline=self.o4.pk, data=self.data, extra=self.extra)
        self.response_403()
        assert before_create == CharacterInstance.objects.filter(character=self.c1).count()

    def test_object_permissions(self):
        '''
        Ensure that only an authorized user can create this object.
        '''
        before_create = CharacterInstance.objects.filter(character=self.c1).count()
        for user in self.naughty_users:
            with self.login(username=user.username):
                self.post('fiction_outlines_api:character_instance_create', character=self.c1.pk,
                          outline=self.o4.pk, data=self.data, extra=self.extra)
                self.response_403()
                assert before_create == CharacterInstance.objects.filter(character=self.c1).count()

    def test_invalid_submission(self):
        '''
        Ensure the unique together is enforced.
        '''
        before_create = CharacterInstance.objects.filter(character=self.c1).count()
        with self.login(username=self.user1.username):
            self.post('fiction_outlines_api:character_instance_create', character=self.c1.pk,
                      outline=self.o1.pk, data=self.data, extra=self.extra)
            self.response_400()
            assert before_create == CharacterInstance.objects.filter(character=self.c1).count()

    def test_valid_submission(self):
        '''
        Confirm that authorized user is allowed to do legal creations.
        '''
        before_create = CharacterInstance.objects.filter(character=self.c1).count()
        with self.login(username=self.user1.username):
            self.post('fiction_outlines_api:character_instance_create', character=self.c1.pk,
                      outline=self.o4.pk, data=self.data, extra=self.extra)
            self.response_201()
            assert CharacterInstance.objects.filter(character=self.c1).count() - before_create == 1


class CharacterInstanceDetailTest(FictionOutlineAbstractTestCase):
    '''
    Character Instance detail retrieval test.
    '''

    def test_login_required(self):
        '''
        You have to be logged in.
        '''
        self.get('fiction_outlines_api:character_instance_item', character=self.c1.pk,
                 instance=self.c1int.pk, extra=self.extra)
        self.response_403()

    def test_object_permissions(self):
        '''
        Ensure unauthorized users cannot access object.
        '''
        for user in self.naughty_users:
            with self.login(username=user.username):
                self.get('fiction_outlines_api:character_instance_item', character=self.c1.pk,
                         instance=self.c1int.pk, extra=self.extra)
                self.response_403()

    def test_authorized_user(self):
        '''
        Ensure authorized user can access.
        '''
        with self.login(username=self.user1.username):
            self.get('fiction_outlines_api:character_instance_item', character=self.c1.pk,
                     instance=self.c1int.pk, extra=self.extra)
            self.response_200()
            assert CharacterInstanceSerializer(self.c1int).data == self.last_response.data


class CharacterInstanceUpdateTest(FictionOutlineAbstractTestCase):
    '''
    Test cases for detail updating on character instance objects.
    '''

    def setUp(self):
        super().setUp()
        self.long_data = {
            'main_character': True,
            'pov_character': True,
            'protagonist': True,
            'antagonist': False,
            'obstacle': False,
            'villain': False
        }
        self.short_data = {'obstacle': True}

    def test_login_required(self):
        '''
        You have be logged in.
        '''
        self.put('fiction_outlines_api:character_instance_item', character=self.c1.pk,
                 instance=self.c1int.pk, data=self.long_data, extra=self.extra)
        self.response_403()
        assert self.c1int.main_character == CharacterInstance.objects.get(pk=self.c1int.pk).main_character
        self.patch('fiction_outlines_api:character_instance_item', character=self.c1.pk,
                   instance=self.c1int.pk, data=self.short_data, extra=self.extra)
        self.response_403()
        assert self.c1int.obstacle == CharacterInstance.objects.get(pk=self.c1int.pk).obstacle

    def test_object_permissions(self):
        '''
        Ensure that only authorized users can edit this object.
        '''
        for user in self.naughty_users:
            with self.login(username=user.username):
                self.put('fiction_outlines_api:character_instance_item', character=self.c1.pk,
                         instance=self.c1int.pk, data=self.long_data, extra=self.extra)
                self.response_403()
                assert self.c1int.main_character == CharacterInstance.objects.get(pk=self.c1int.pk).main_character
                self.patch('fiction_outlines_api:character_instance_item', character=self.c1.pk,
                           instance=self.c1int.pk, data=self.short_data, extra=self.extra)
                self.response_403()
                assert self.c1int.obstacle == CharacterInstance.objects.get(pk=self.c1int.pk).obstacle

    def test_authorized_user(self):
        '''
        Test that autorized user can make the edits.
        '''
        with self.login(username=self.user1.username):
            self.put('fiction_outlines_api:character_instance_item', character=self.c1.pk,
                     instance=self.c1int.pk, data=self.long_data, extra=self.extra)
            self.response_200()
            assert self.c1int.main_character != CharacterInstance.objects.get(pk=self.c1int.pk).main_character
            self.patch('fiction_outlines_api:character_instance_item', character=self.c1.pk,
                       instance=self.c1int.pk, data=self.short_data, extra=self.extra)
            self.response_200()
            assert self.c1int.obstacle != CharacterInstance.objects.get(pk=self.c1int.pk).obstacle


class CharacterInstanceDeleteTest(FictionOutlineAbstractTestCase):
    '''
    Test cases for Character instance deletion
    '''

    def test_login_required(self):
        '''
        You have to be logged in.
        '''
        self.delete('fiction_outlines_api:character_instance_item', character=self.c1.pk,
                    instance=self.c1int.pk, extra=self.extra)
        self.response_403()
        assert CharacterInstance.objects.get(pk=self.c1int.pk)

    def test_object_permissions(self):
        '''
        Ensure unauthorized users cannot delete the object.
        '''
        for user in self.naughty_users:
            with self.login(username=user.username):
                self.delete('fiction_outlines_api:character_instance_item', character=self.c1.pk,
                            instance=self.c1int.pk, extra=self.extra)
                self.response_403()
                assert CharacterInstance.objects.get(pk=self.c1int.pk)

    def test_authorized_user(self):
        '''
        Test authorized user can delete the object.
        '''
        with self.login(username=self.user1.username):
            self.delete('fiction_outlines_api:character_instance_item', character=self.c1.pk,
                        instance=self.c1int.pk, extra=self.extra)
            self.response_204()
            with pytest.raises(ObjectDoesNotExist):
                CharacterInstance.objects.get(pk=self.c1int.pk)


# Location Object tests


class LocationListTestCase(FictionOutlineAbstractTestCase):
    '''
    Test case for location listing.
    '''

    def test_login_required(self):
        '''
        You have to be logged in.
        '''
        self.get('fiction_outlines_api:location_listcreate')
        self.response_403()

    def test_authenticated_user(self):
        '''
        Ensure that users cannot see location that another owns.
        '''
        forbidden_character = LocationSerializer(Location.objects.filter(user=self.user1), many=True)
        for user in self.naughty_users:
            with self.login(username=user.username):
                self.assertGoodView('fiction_outlines_api:location_listcreate')
                results = self.last_response.data
                for fs in forbidden_character.data:
                    assert fs not in results
        with self.login(username=self.user1.username):
            self.assertGoodView('fiction_outlines_api:location_listcreate')
            results = self.last_response.data
            for fs in forbidden_character.data:
                assert fs in results


class LocationCreateTestCase(FictionOutlineAbstractTestCase):
    '''
    Test for API creation of characters.
    '''

    data = {
        'name': 'Margaritaville',
        'description': 'Missing a shaker of salt.',
        'tags': ['your dad', 'parrothead'],
        'series': []
    }

    def setUp(self):
        super().setUp()
        self.data['series'] = [self.s1.pk, ]

    def test_login_required(self):
        '''
        you have to be logged in.
        '''
        self.post('fiction_outlines_api:location_listcreate', data=self.data, extra=self.extra)
        self.response_403()

    def test_invalid_series(self):
        '''
        Verify that an invalid series is rejected.
        '''
        before_create = Location.objects.filter(user=self.user1).count()
        with self.login(username=self.user1.username):
            self.data['series'].append(self.s3.pk)
            self.post('fiction_outlines_api:location_listcreate', data=self.data, extra=self.extra)
            self.response_403()
            assert before_create == Location.objects.filter(user=self.user1).count()

    def test_authenticated_user(self):
        before_create = Location.objects.filter(user=self.user1).count()
        with self.login(username=self.user1.username):
            self.post('fiction_outlines_api:location_listcreate', data=self.data, extra=self.extra)
            print(self.last_response.content)
            self.response_201()
            assert Location.objects.filter(user=self.user1).count() - before_create == 1
            latest = Location.objects.latest('created')
            assert 'Margaritaville' == latest.name
            assert latest.tags.count() == 2
            data2 = {
                'name': 'Temp location',
                'description': "I have no series",
                'tags': ['test', 'yup'],
                'series': []
            }
            self.post('fiction_outlines_api:location_listcreate', data=data2, extra=self.extra)
            print(self.last_response.content)
            self.response_201()
            assert Location.objects.filter(user=self.user1).count() - before_create == 2
            latest = Location.objects.latest('created')
            assert 'Temp location' == latest.name
            assert latest.tags.count() == 2


class LocationDetailTestCase(FictionOutlineAbstractTestCase):
    '''
    Tests for viewing location details.
    '''

    def test_login_required(self):
        '''
        You have to be logged in.
        '''
        self.get('fiction_outlines_api:location_item', location=self.l1.pk, extra=self.extra)
        self.response_403()

    def test_object_permissions(self):
        '''
        Ensure an unauthorized user cannot access the items.
        '''
        for user in self.naughty_users:
            with self.login(username=user.username):
                self.get('fiction_outlines_api:location_item', location=self.l1.pk, extra=self.extra)
                self.response_403()

    def test_authorized_user(self):
        '''
        Verify that authorized user can access the item.
        '''
        with self.login(username=self.user1.username):
            self.assertGoodView('fiction_outlines_api:location_item', location=self.l1.pk, extra=self.extra)
            serialized_object = LocationSerializer(self.l1)
            assert serialized_object.data == self.last_response.data
            assert (len(self.last_response.data['location_instances']) ==
                    LocationInstance.objects.filter(location=self.l1).count())


class LocationUpdateView(FictionOutlineAbstractTestCase):
    '''
    Tests for location update functions, both PUT and PATCH.
    '''
    short_data = {'name': 'The seekrit place'}
    long_data = {
        'name': 'Tactical Blanket Fort',
        'description': "So cozy, and safe.",
        'tags': ['cuddles', ],
        'series': []
    }

    def setUp(self):
        super().setUp()
        self.long_data['series'] = [self.s1.pk, ]

    def test_login_required(self):
        '''
        You have to be logged in.
        '''
        self.put('fiction_outlines_api:location_item', location=self.l1.pk, data=self.long_data, extra=self.extra)
        self.response_403()
        assert self.l1.name == Location.objects.get(pk=self.l1.pk).name
        self.patch('fiction_outlines_api:location_item', location=self.l1.pk, data=self.short_data, extra=self.extra)
        self.response_403()
        assert self.l1.name == Location.objects.get(pk=self.l1.pk).name

    def test_object_permissions(self):
        '''
        Ensure that an unauthorized user cannot edit the object.
        '''
        for user in [self.user2, self.user2]:
            with self.login(username=user.username):
                self.put('fiction_outlines_api:location_item', location=self.l1.pk,
                         data=self.long_data, extra=self.extra)
                self.response_403()
                assert self.l1.name == Location.objects.get(pk=self.l1.pk).name
                self.patch('fiction_outlines_api:location_item', location=self.l1.pk,
                           data=self.short_data, extra=self.extra)
                self.response_403()
                assert self.l1.name == Location.objects.get(pk=self.l1.pk).name

    def test_invalid_series(self):
        '''
        Prevent a user from associating a location with a series for which they
        don't have editing rights.
        '''
        with self.login(username=self.user1.username):
            self.long_data['series'].append(self.s3.pk)
            self.put('fiction_outlines_api:location_item', location=self.l1.pk,
                     data=self.long_data, extra=self.extra)
            self.response_403()
            assert self.l1.series.count() == Location.objects.get(pk=self.l1.pk).series.count()
            self.patch('fiction_outlines_api:location_item', location=self.l1.pk,
                       data={'series': [self.s3.pk, ]}, extra=self.extra)
            self.response_403()
            assert self.l1.series.count() == Location.objects.get(pk=self.l1.pk).series.count()

    def test_authorized_user(self):
        '''
        Ensure that an authorized user can make the necessary edits.
        '''
        with self.login(username=self.user1.username):
            self.patch('fiction_outlines_api:location_item', location=self.l1.pk,
                       data=self.short_data, extra=self.extra)
            self.response_200()
            patched_l1 = Location.objects.get(pk=self.l1.pk)
            assert patched_l1.name == 'The seekrit place'
            assert not patched_l1.description
            self.put('fiction_outlines_api:location_item', location=self.l1.pk,
                     data=self.long_data, extra=self.extra)
            self.response_200()
            put_l1 = Location.objects.get(pk=self.l1.pk)
            assert put_l1.name == 'Tactical Blanket Fort'
            assert put_l1.description
            assert put_l1.tags.count() == 1
            self.patch('fiction_outlines_api:location_item', location=self.l1.pk,
                       data={'series': []}, extra=self.extra)
            self.response_200()
            assert not Location.objects.get(pk=self.l1.pk).series.count()


class LocationDeleteTest(FictionOutlineAbstractTestCase):
    '''
    Test location deletion.
    '''

    def test_login_required(self):
        '''
        You have to be logged in.
        '''
        self.delete('fiction_outlines_api:location_item', location=self.l1.pk, extra=self.extra)
        self.response_403()
        assert Location.objects.get(pk=self.l1.pk)

    def test_unauthorized_users(self):
        '''
        Ensure unauthorized users cannot delete the object.
        '''
        for user in self.naughty_users:
            with self.login(username=user.username):
                self.delete('fiction_outlines_api:location_item', location=self.l1.pk, extra=self.extra)
                self.response_403()
                assert Location.objects.get(pk=self.l1.pk)

    def test_authorized_user(self):
        '''
        Test that an authroized user can delete as expected.
        '''
        with self.login(username=self.user1.username):
            self.delete('fiction_outlines_api:location_item', location=self.l1.pk, extra=self.extra)
            self.response_204()
            with pytest.raises(ObjectDoesNotExist):
                Location.objects.get(pk=self.l1.pk)


# LocationInstance tests


class LocationInstanceCreateTest(FictionOutlineAbstractTestCase):
    '''
    Test case for creating location instances.
    '''

    def setUp(self):
        super().setUp()
        self.o4 = Outline(title="Test valid outline", description='Hi there.', user=self.user1)
        self.o4.save()

    def test_login_required(self):
        '''
        You have to be logged in.
        '''
        before_create = LocationInstance.objects.filter(location=self.l1).count()
        self.post('fiction_outlines_api:location_instance_create', location=self.l1.pk,
                  outline=self.o4.pk, extra=self.extra)
        self.response_403()
        assert before_create == LocationInstance.objects.filter(location=self.l1).count()

    def test_object_permissions(self):
        '''
        Ensure that only an authorized user can create this object.
        '''
        before_create = LocationInstance.objects.filter(location=self.l1).count()
        for user in self.naughty_users:
            with self.login(username=user.username):
                self.post('fiction_outlines_api:location_instance_create', location=self.l1.pk,
                          outline=self.o4.pk, extra=self.extra)
                self.response_403()
                assert before_create == LocationInstance.objects.filter(location=self.l1).count()

    def test_invalid_submission(self):
        '''
        Ensure the unique together is enforced.
        '''
        before_create = LocationInstance.objects.filter(location=self.l1).count()
        with self.login(username=self.user1.username):
            self.post('fiction_outlines_api:location_instance_create', location=self.l1.pk,
                      outline=self.o1.pk, extra=self.extra)
            self.response_400()
            assert before_create == LocationInstance.objects.filter(location=self.l1).count()

    def test_valid_submission(self):
        '''
        Confirm that authorized user is allowed to do legal creations.
        '''
        before_create = LocationInstance.objects.filter(location=self.l1).count()
        with self.login(username=self.user1.username):
            self.post('fiction_outlines_api:location_instance_create', location=self.l1.pk,
                      outline=self.o4.pk, extra=self.extra)
            self.response_201()
            assert LocationInstance.objects.filter(location=self.l1).count() - before_create == 1


class LocationInstanceDetailTest(FictionOutlineAbstractTestCase):
    '''
    Location Instance detail retrieval test.
    '''

    def test_login_required(self):
        '''
        You have to be logged in.
        '''
        self.get('fiction_outlines_api:location_instance_item', location=self.l1.pk,
                 instance=self.l1int.pk, extra=self.extra)
        self.response_403()

    def test_object_permissions(self):
        '''
        Ensure unauthorized users cannot access object.
        '''
        for user in self.naughty_users:
            with self.login(username=user.username):
                self.get('fiction_outlines_api:location_instance_item', location=self.l1.pk,
                         instance=self.l1int.pk, extra=self.extra)
                self.response_403()

    def test_authorized_user(self):
        '''
        Ensure authorized user can access.
        '''
        with self.login(username=self.user1.username):
            self.get('fiction_outlines_api:location_instance_item', location=self.l1.pk,
                     instance=self.l1int.pk, extra=self.extra)
            self.response_200()
            assert LocationInstanceSerializer(self.l1int).data == self.last_response.data


class LocationInstanceDeleteTest(FictionOutlineAbstractTestCase):
    '''
    Test cases for Location instance deletion
    '''

    def test_login_required(self):
        '''
        You have to be logged in.
        '''
        self.delete('fiction_outlines_api:location_instance_item', location=self.l1.pk,
                    instance=self.l1int.pk, extra=self.extra)
        self.response_403()
        assert LocationInstance.objects.get(pk=self.l1int.pk)

    def test_object_permissions(self):
        '''
        Ensure unauthorized users cannot delete the object.
        '''
        for user in self.naughty_users:
            with self.login(username=user.username):
                self.delete('fiction_outlines_api:location_instance_item', location=self.l1.pk,
                            instance=self.l1int.pk, extra=self.extra)
                self.response_403()
                assert LocationInstance.objects.get(pk=self.l1int.pk)

    def test_authorized_user(self):
        '''
        Test authorized user can delete the object.
        '''
        with self.login(username=self.user1.username):
            self.delete('fiction_outlines_api:location_instance_item', location=self.l1.pk,
                        instance=self.l1int.pk, extra=self.extra)
            self.response_204()
            with pytest.raises(ObjectDoesNotExist):
                LocationInstance.objects.get(pk=self.l1int.pk)


# Outline Object tests


class OutlineListTestCase(FictionOutlineAbstractTestCase):
    '''
    Test case for outline listing.
    '''

    def test_login_required(self):
        '''
        You have to be logged in.
        '''
        self.get('fiction_outlines_api:outline_listcreate')
        self.response_403()

    def test_authenticated_user(self):
        '''
        Ensure that users cannot see outline that another owns.
        '''
        forbidden_character = OutlineSerializer(Outline.objects.filter(user=self.user1), many=True)
        for user in self.naughty_users:
            with self.login(username=user.username):
                self.assertGoodView('fiction_outlines_api:outline_listcreate')
                results = self.last_response.data
                for fs in forbidden_character.data:
                    assert fs not in results
        with self.login(username=self.user1.username):
            self.assertGoodView('fiction_outlines_api:outline_listcreate')
            results = self.last_response.data
            for fs in forbidden_character.data:
                assert fs in results


class OutlineCreateTestCase(FictionOutlineAbstractTestCase):
    '''
    Test for API creation of characters.
    '''

    data = {
        'title': 'My Opus',
        'description': 'Not the penguin. A work of art.',
        'tags': ['antartica', ],
        'series': None
    }

    def setUp(self):
        super().setUp()
        self.data['series'] = self.s1.pk

    def test_login_required(self):
        '''
        you have to be logged in.
        '''
        self.post('fiction_outlines_api:outline_listcreate', data=self.data, extra=self.extra)
        self.response_403()

    def test_invalid_series(self):
        '''
        Verify that an invalid series is rejected.
        '''
        before_create = Outline.objects.filter(user=self.user1).count()
        with self.login(username=self.user1.username):
            self.data['series'] = self.s3.pk
            self.post('fiction_outlines_api:outline_listcreate', data=self.data, extra=self.extra)
            self.response_403()
            assert before_create == Outline.objects.filter(user=self.user1).count()

    def test_authenticated_user(self):
        before_create = Outline.objects.filter(user=self.user1).count()
        with self.login(username=self.user1.username):
            self.post('fiction_outlines_api:outline_listcreate', data=self.data, extra=self.extra)
            print(self.last_response.content)
            self.response_201()
            assert Outline.objects.filter(user=self.user1).count() - before_create == 1
            latest = Outline.objects.latest('created')
            assert 'My Opus' == latest.title
            assert latest.tags.count() == 1
            data2 = {
                'title': 'One shot',
                'description': 'An outline without a series',
                'tags': ['fledgling', 'nonfranchise'],
                'series': None
            }
            self.post('fiction_outlines_api:outline_listcreate', data=data2, extra=self.extra)
            self.response_201()
            assert Outline.objects.filter(user=self.user1).count() - before_create == 2
            latest = Outline.objects.latest('created')
            assert 'One shot' == latest.title


class OutlineDetailTestCase(FictionOutlineAbstractTestCase):
    '''
    Tests for viewing outline details.
    '''

    def setUp(self):
        super().setUp()
        self.chap1 = self.o2.story_tree_root.add_child(story_element_type='chapter',
                                                       name='chapter 1', description='yep')
        self.scene1 = self.chap1.add_child(story_element_type='ss', name='scene1', description="I'm advanced!")

    def test_login_required(self):
        '''
        You have to be logged in.
        '''
        self.get('fiction_outlines_api:outline_item', outline=self.o1.pk, extra=self.extra)
        self.response_403()

    def test_object_permissions(self):
        '''
        Ensure an unauthorized user cannot access the items.
        '''
        for user in self.naughty_users:
            with self.login(username=user.username):
                self.get('fiction_outlines_api:outline_item', outline=self.o1.pk, extra=self.extra)
                self.response_403()

    def test_authorized_user(self):
        '''
        Verify that authorized user can access the item.
        '''
        with self.login(username=self.user1.username):
            self.assertGoodView('fiction_outlines_api:outline_item', outline=self.o1.pk, extra=self.extra)
            serialized_object = OutlineSerializer(self.o1)
            assert serialized_object.data == self.last_response.data
            assert self.o1.arc_set.count() == len(self.last_response.data['arc_set'])
            assert (len(StoryElementNode.get_annotated_list(self.o1.story_tree_root)[1:]) ==
                    len(self.last_response.data['outline_structure']))
            self.assertGoodView('fiction_outlines_api:outline_item', outline=self.o2.pk, extra=self.extra)
            serialized_object = OutlineSerializer(self.o2)
            assert serialized_object.data == self.last_response.data
            assert (len(StoryElementNode.get_annotated_list(self.o2.story_tree_root)[1:]) ==
                    len(self.last_response.data['outline_structure']))


class OutlineUpdateView(FictionOutlineAbstractTestCase):
    '''
    Tests for outline update functions, both PUT and PATCH.
    '''
    short_data = {'title': 'Dark Memoir'}
    long_data = {
        'title': 'Grandpa digs in snow',
        'description': "Did you know that writing tests can be a *bit* boring?",
        'tags': ['clowns', 'no sleep'],
        'series': None,
    }

    def setUp(self):
        super().setUp()
        self.long_data['series'] = self.s2.pk

    def test_login_required(self):
        '''
        You have to be logged in.
        '''
        self.put('fiction_outlines_api:outline_item', outline=self.o1.pk, data=self.long_data, extra=self.extra)
        self.response_403()
        assert self.o1.title == Outline.objects.get(pk=self.o1.pk).title
        self.patch('fiction_outlines_api:outline_item', outline=self.o1.pk, data=self.short_data, extra=self.extra)
        self.response_403()
        assert self.o1.title == Outline.objects.get(pk=self.o1.pk).title

    def test_object_permissions(self):
        '''
        Ensure that an unauthorized user cannot edit the object.
        '''
        for user in [self.user2, self.user2]:
            with self.login(username=user.username):
                self.put('fiction_outlines_api:outline_item', outline=self.o1.pk,
                         data=self.long_data, extra=self.extra)
                self.response_403()
                assert self.o1.title == Outline.objects.get(pk=self.o1.pk).title
                self.patch('fiction_outlines_api:outline_item', outline=self.o1.pk,
                           data=self.short_data, extra=self.extra)
                self.response_403()
                assert self.o1.title == Outline.objects.get(pk=self.o1.pk).title

    def test_invalid_series(self):
        '''
        Verify that an invalid series is rejected.
        '''
        with self.login(username=self.user1.username):
            self.long_data['series'] = self.s3.pk
            self.put('fiction_outlines_api:outline_item', outline=self.o1.pk,
                     data=self.long_data, extra=self.extra)
            self.response_403()
            assert self.o1.series == Outline.objects.get(pk=self.o1.pk).series

    def test_authorized_user(self):
        '''
        Ensure that an authorized user can make the necessary edits.
        '''
        with self.login(username=self.user1.username):
            self.patch('fiction_outlines_api:outline_item', outline=self.o1.pk,
                       data=self.short_data, extra=self.extra)
            self.response_200()
            patched_o1 = Outline.objects.get(pk=self.o1.pk)
            assert patched_o1.title == 'Dark Memoir'
            assert not patched_o1.description
            self.put('fiction_outlines_api:outline_item', outline=self.o1.pk,
                     data=self.long_data, extra=self.extra)
            self.response_200()
            put_o1 = Outline.objects.get(pk=self.o1.pk)
            assert put_o1.title == 'Grandpa digs in snow'
            assert put_o1.description
            assert put_o1.tags.count() == 2


class OutlineDeleteTest(FictionOutlineAbstractTestCase):
    '''
    Test outline deletion.
    '''

    def test_login_required(self):
        '''
        You have to be logged in.
        '''
        self.delete('fiction_outlines_api:outline_item', outline=self.o1.pk, extra=self.extra)
        self.response_403()
        assert Outline.objects.get(pk=self.o1.pk)

    def test_unauthorized_users(self):
        '''
        Ensure unauthorized users cannot delete the object.
        '''
        for user in self.naughty_users:
            with self.login(username=user.username):
                self.delete('fiction_outlines_api:outline_item', outline=self.o1.pk, extra=self.extra)
                self.response_403()
                assert Outline.objects.get(pk=self.o1.pk)

    def test_authorized_user(self):
        '''
        Test that an authroized user can delete as expected.
        '''
        with self.login(username=self.user1.username):
            self.delete('fiction_outlines_api:outline_item', outline=self.o1.pk, extra=self.extra)
            self.response_204()
            with pytest.raises(ObjectDoesNotExist):
                Outline.objects.get(pk=self.o1.pk)


class ArcCreateTest(FictionOutlineAbstractTestCase):
    '''
    Test creating an arc.
    '''
    data = {
        'name': 'Coming of age',
        'mace_type': 'milieu',
    }

    def test_require_login(self):
        '''
        You have to be logged in.
        '''
        before_create = Arc.objects.filter(outline=self.o1).count()
        self.post('fiction_outlines_api:arc_create', outline=self.o1.pk, data=self.data, extra=self.extra)
        self.response_403()
        assert before_create == Arc.objects.filter(outline=self.o1).count()

    def test_object_permissions(self):
        for user in self.naughty_users:
            with self.login(username=user.username):
                before_create = Arc.objects.filter(outline=self.o1).count()
                self.post('fiction_outlines_api:arc_create', outline=self.o1.pk, data=self.data, extra=self.extra)
                self.response_403()
                assert before_create == Arc.objects.filter(outline=self.o1).count()

    def test_authorized_user(self):
        '''
        Test creation of an arc from an authorized user.
        '''
        with self.login(username=self.user1.username):
            before_create = Arc.objects.filter(outline=self.o1).count()
            self.post('fiction_outlines_api:arc_create', outline=self.o1.pk, data=self.data, extra=self.extra)
            self.response_201()
            assert Arc.objects.filter(outline=self.o1).count() - before_create == 1


class ArcDetailTest(FictionOutlineAbstractTestCase):
    '''
    Test detail view for arc.
    '''

    def test_require_login(self):
        '''
        You have to be authenticated.
        '''
        self.get('fiction_outlines_api:arc_item', outline=self.o1.pk, arc=self.arc1.pk, extra=self.extra)
        self.response_403()

    def test_object_permissions(self):
        '''
        Ensure that only users with the right permissions can access the object.
        '''
        for user in self.naughty_users:
            with self.login(username=user.username):
                self.get('fiction_outlines_api:arc_item', outline=self.o1.pk, arc=self.arc1.pk, extra=self.extra)
                self.response_403()

    def test_authorized_user(self):
        '''
        Test that authorized user can access the data as expected.
        '''
        with self.login(username=self.user1.username):
            self.get('fiction_outlines_api:arc_item', outline=self.o1.pk, arc=self.arc1.pk, extra=self.extra)
            self.response_200()
            assert ArcSerializer(self.arc1).data == self.last_response.data
            assert (len(ArcElementNode.get_annotated_list(self.arc1.arc_root_node)[1:]) ==
                    len(self.last_response.data['arc_structure']))


class ArcUpdateTest(FictionOutlineAbstractTestCase):
    '''
    Test updating of an Arc.
    '''

    def setUp(self):
        super().setUp()
        self.long_data = {
            'name': 'Lost in tests',
            'mace_type': 'milieu',
        }
        self.short_data = {
            'name': 'HELLLLLLLLLLLO'
        }

    def test_requires_login(self):
        '''
        You have to be logged in.
        '''
        self.put('fiction_outlines_api:arc_item', outline=self.o1.pk,
                 arc=self.arc1.pk, data=self.long_data, extra=self.extra)
        self.response_403()
        assert self.arc1.name == Arc.objects.get(pk=self.arc1.pk).name
        self.patch('fiction_outlines_api:arc_item', outline=self.o1.pk,
                   arc=self.arc1.pk, data=self.short_data, extra=self.extra)
        self.response_403()
        assert self.arc1.name == Arc.objects.get(pk=self.arc1.pk).name

    def test_object_permissions(self):
        for user in self.naughty_users:
            with self.login(username=user.username):
                self.put('fiction_outlines_api:arc_item', outline=self.o1.pk,
                         arc=self.arc1.pk, data=self.long_data, extra=self.extra)
                self.response_403()
                assert self.arc1.name == Arc.objects.get(pk=self.arc1.pk).name
                self.patch('fiction_outlines_api:arc_item', outline=self.o1.pk,
                           arc=self.arc1.pk, data=self.short_data, extra=self.extra)
                self.response_403()
                assert self.arc1.name == Arc.objects.get(pk=self.arc1.pk).name

    def test_authorized_user(self):
        '''
        An authroized user can make changes.
        '''
        with self.login(username=self.user1.username):
            self.patch('fiction_outlines_api:arc_item', outline=self.o1.pk,
                       arc=self.arc1.pk, data=self.short_data, extra=self.extra)
            self.response_200()
            assert Arc.objects.get(pk=self.arc1.pk).name == 'HELLLLLLLLLLLO'
            self.put('fiction_outlines_api:arc_item', outline=self.o1.pk,
                     arc=self.arc1.pk, data=self.long_data, extra=self.extra)
            self.response_200()
            updated_arc = Arc.objects.get(pk=self.arc1.pk)
            assert updated_arc.name == 'Lost in tests'
            assert updated_arc.mace_type == 'milieu'


class ArcDeleteTest(FictionOutlineAbstractTestCase):
    '''
    Test arc deletion API calls
    '''

    def test_login_required(self):
        '''
        You have to be logged in.
        '''
        self.delete('fiction_outlines_api:arc_item', outline=self.o1.pk,
                    arc=self.arc1.pk, extra=self.extra)
        self.response_403()
        assert Arc.objects.get(pk=self.arc1.pk)

    def test_object_permissions(self):
        '''
        Ensure that only an authorized user can delete an arc.
        '''
        for user in self.naughty_users:
            with self.login(username=user.username):
                self.delete('fiction_outlines_api:arc_item', outline=self.o1.pk,
                            arc=self.arc1.pk, extra=self.extra)
                self.response_403()
                assert Arc.objects.get(pk=self.arc1.pk)

    def test_authorized_user(self):
        '''
        Test that authorized user can delete arc.
        '''
        with self.login(username=self.user1.username):
            self.delete('fiction_outlines_api:arc_item', outline=self.o1.pk,
                        arc=self.arc1.pk, extra=self.extra)
            self.response_204()
            with pytest.raises(ObjectDoesNotExist):
                Arc.objects.get(pk=self.arc1.pk)


# Tree-based Test cases.


class ArcNodeAbstractTestCase(FictionOutlineAbstractTestCase):
    '''
    Adds additional properties to test.
    '''

    def setUp(self):
        super().setUp()
        self.node_to_test = self.arc1.arc_root_node.get_children()[0]
        self.part1 = self.o1.story_tree_root.add_child(
            name='Part 1', description='A long time ago in a galaxy far away', story_element_type='part')
        self.o1_valid_storynode = self.part1.add_child(
            name='Chapter One', story_element_type='chapter', description='Our story begins')
        logger.debug('self.o1_valid_storynode is a node of type \'%s\' and has a pk of %s' %
                     (self.o1_valid_storynode.story_element_type, self.o1_valid_storynode.pk))
        self.o1_invalid_node = self.o2.story_tree_root.add_child(name='Chapter One', story_element_type='chapter',
                                                                 description='A totally different story begins.')


class ArcNodeDetailTest(ArcNodeAbstractTestCase):
    '''
    Tests for arcnode retrieval.
    '''
    def test_require_login(self):
        '''
        You have be logged in.
        '''
        self.get('fiction_outlines_api:arcnode_item', outline=self.o1.pk,
                 arc=self.arc1.pk, arcnode=self.node_to_test.pk, extra=self.extra)
        self.response_403()

    def test_object_permissions(self):
        '''
        Verify that a user with incorrect permissions cannot access this object.
        '''
        for user in self.naughty_users:
            with self.login(username=user.username):
                self.get('fiction_outlines_api:arcnode_item', outline=self.o1.pk,
                         arc=self.arc1.pk, arcnode=self.node_to_test.pk, extra=self.extra)
                self.response_403()

    def test_authorized_user(self):
        '''
        Verify that an authorized user can access the required object.
        '''
        with self.login(username=self.user1.username):
            self.get('fiction_outlines_api:arcnode_item', outline=self.o1.pk,
                     arc=self.arc1.pk, arcnode=self.node_to_test.pk, extra=self.extra)
            self.response_200()
            assert ArcElementNodeSerializer(self.node_to_test).data == self.last_response.data


class ArcNodeUpdateTest(ArcNodeAbstractTestCase):
    '''
    Test cases for updating arc nodes.
    '''

    def setUp(self):
        super().setUp()
        self.long_data = {
            'arc_element_type': 'mile_hook',
            'description': 'Our hero begins their story',
            'story_element_node': self.o1_valid_storynode.pk,
            'assoc_characters': [self.c1int.pk],
            'assoc_locations': [self.l1int.pk],
        }
        self.short_data = {'description': 'I ate a funky monkey.'}

    def test_login_required(self):
        '''
        You have to be logged in.
        '''
        self.put('fiction_outlines_api:arcnode_item', outline=self.o1.pk, arc=self.arc1.pk,
                 arcnode=self.node_to_test.pk, data=self.long_data, extra=self.extra)
        self.response_403()
        assert self.node_to_test.description == ArcElementNode.objects.get(pk=self.node_to_test.pk).description
        self.patch('fiction_outlines_api:arcnode_item', outline=self.o1.pk, arc=self.arc1.pk,
                   arcnode=self.node_to_test.pk, data=self.short_data, extra=self.extra)
        self.response_403()
        assert self.node_to_test.description == ArcElementNode.objects.get(pk=self.node_to_test.pk).description

    def test_object_permissions(self):
        '''
        Ensure that only authorized users can update the object.
        '''
        for user in self.naughty_users:
            with self.login(username=user.username):
                self.put('fiction_outlines_api:arcnode_item', outline=self.o1.pk, arc=self.arc1.pk,
                         arcnode=self.node_to_test.pk, data=self.long_data, extra=self.extra)
                self.response_403()
                assert self.node_to_test.description == ArcElementNode.objects.get(pk=self.node_to_test.pk).description
                self.patch('fiction_outlines_api:arcnode_item', outline=self.o1.pk, arc=self.arc1.pk,
                           arcnode=self.node_to_test.pk, data=self.short_data, extra=self.extra)
                self.response_403()
                assert self.node_to_test.description == ArcElementNode.objects.get(pk=self.node_to_test.pk).description

    def test_invalid_submission(self):
        '''
        Ensure that validation prevents incorrect records.
        '''
        with self.login(username=self.user1.username):
            bad_data = self.long_data
            bad_data['assoc_characters'] = [self.c1int2.pk]
            bad_data['assoc_locations'] = [self.l1int2.pk]
            self.put('fiction_outlines_api:arcnode_item', outline=self.o1.pk, arc=self.arc1.pk,
                     arcnode=self.node_to_test.pk, data=bad_data, extra=self.extra)
            self.response_400()
            assert (self.node_to_test.assoc_characters.count() ==
                    ArcElementNode.objects.get(pk=self.node_to_test.pk).assoc_characters.count())
            new_bad_data = self.long_data
            new_bad_data['story_element_node'] = self.o1_invalid_node.pk
            self.put('fiction_outlines_api:arcnode_item', outline=self.o1.pk, arc=self.arc1.pk,
                     arcnode=self.node_to_test.pk, data=new_bad_data, extra=self.extra)
            self.response_400()
            assert not ArcElementNode.objects.get(pk=self.node_to_test.pk).story_element_node

    def test_valid_submission(self):
        '''
        Ensure that the authorized user can make valid edits.
        '''
        with self.login(username=self.user1.username):
            self.patch('fiction_outlines_api:arcnode_item', outline=self.o1.pk, arc=self.arc1.pk,
                       arcnode=self.node_to_test.pk, data=self.short_data, extra=self.extra)
            self.response_200()
            assert ArcElementNode.objects.get(pk=self.node_to_test.pk).description == 'I ate a funky monkey.'
            self.put('fiction_outlines_api:arcnode_item', outline=self.o1.pk, arc=self.arc1.pk,
                     arcnode=self.node_to_test.pk, data=self.long_data, extra=self.extra)
            self.response_200()
            updated_node = ArcElementNode.objects.get(pk=self.node_to_test.pk)
            assert updated_node.story_element_node == self.o1_valid_storynode
            assert self.c1int in updated_node.assoc_characters.all()
            assert self.l1int in updated_node.assoc_locations.all()


class ArcNodeDeleteTest(ArcNodeAbstractTestCase):
    '''
    Test deletion rules for an arcnode
    '''
    def setUp(self):
        super().setUp()
        self.hook = self.node_to_test
        self.reso = self.arc1.arc_root_node.get_children()[6]
        self.pt1 = self.arc1.arc_root_node.get_children()[1]

    def test_login_required(self):
        '''
        You have to be logged in.
        '''
        self.delete('fiction_outlines_api:arcnode_item', outline=self.o1.pk, arc=self.arc1.pk,
                    arcnode=self.pt1.pk, extra=self.extra)
        self.response_403()
        assert ArcElementNode.objects.get(pk=self.pt1.pk)

    def test_object_permissions(self):
        '''
        Ensure that unauthorized users cannot delete.
        '''
        for user in self.naughty_users:
            with self.login(username=user.username):
                self.delete('fiction_outlines_api:arcnode_item', outline=self.o1.pk, arc=self.arc1.pk,
                            arcnode=self.pt1.pk, extra=self.extra)
                self.response_403()
                assert ArcElementNode.objects.get(pk=self.pt1.pk)

    def test_invalid_deletion_requests(self):
        '''
        Ensure that an authorized user cannot explicitly delete the hook or
        resolution.
        '''
        with self.login(username=self.user1.username):
            self.delete('fiction_outlines_api:arcnode_item', outline=self.o1.pk, arc=self.arc1.pk,
                        arcnode=self.hook.pk, extra=self.extra)
            self.response_400()
            assert ArcElementNode.objects.get(pk=self.hook.pk)
            self.delete('fiction_outlines_api:arcnode_item', outline=self.o1.pk, arc=self.arc1.pk,
                        arcnode=self.reso.pk, extra=self.extra)
            self.response_400()
            assert ArcElementNode.objects.get(pk=self.reso.pk)

    def test_valid_submission(self):
        '''
        Confirm that an authorized user can delete an object with a valid request.
        '''
        with self.login(username=self.user1.username):
            self.delete('fiction_outlines_api:arcnode_item', outline=self.o1.pk, arc=self.arc1.pk,
                        arcnode=self.pt1.pk, extra=self.extra)
            self.response_204()
            with pytest.raises(ObjectDoesNotExist):
                ArcElementNode.objects.get(pk=self.pt1.pk)


class ArcNodeMoveTest(ArcNodeAbstractTestCase):
    '''
    Test for arcnode move operations.
    '''

    def setUp(self):
        super().setUp()
        self.good_move_data = {
            'node_to_move_id': self.node_to_test.pk,
            'target_node_id': self.node_to_test.get_next_sibling().pk,
            'position': 'right',
            'extra': {'format': 'json'}
        }
        self.incompatible_arc_data = {
            'node_to_move_id': self.node_to_test.pk,
            'target_node_id': self.arc2.arc_root_node.get_children()[2].pk,
            'position': 'right',
            'extra': {'format': 'json'}
        }
        new_beat = self.node_to_test.add_child(arc_element_type='beat', description='I am a beat')
        self.illegal_descendant_move_data = {
            'node_to_move_id': self.node_to_test.pk,
            'target_node_id': new_beat.pk,
            'position': 'right',
            'extra': {'format': 'json'}
        }

    def test_login_required(self):
        '''
        You have to be logged in.
        '''
        self.post('fiction_outlines_api:arcnode_move', **self.good_move_data)
        self.response_403()
        assert self.node_to_test.path == ArcElementNode.objects.get(pk=self.node_to_test.pk).path

    def test_object_permissions(self):
        '''
        Ensure unauthorized users cannot move the node.
        '''
        for user in self.naughty_users:
            with self.login(username=user.username):
                self.post('fiction_outlines_api:arcnode_move', **self.good_move_data)
                self.response_403()
                assert self.node_to_test.path == ArcElementNode.objects.get(pk=self.node_to_test.pk).path

    def test_invalid_move(self):
        '''
        Test an invalid move with an authorized user.
        '''
        with self.login(username=self.user1.username):
            self.post('fiction_outlines_api:arcnode_move', **self.incompatible_arc_data)
            self.response_400()
            assert self.node_to_test.path == ArcElementNode.objects.get(pk=self.node_to_test.pk).path
            self.post('fiction_outlines_api:arcnode_move', **self.illegal_descendant_move_data)
            self.response_400()
            assert self.node_to_test.path == ArcElementNode.objects.get(pk=self.node_to_test.pk).path

    def test_valid_move(self):
        '''
        Test a valid move with an authorized user.
        '''
        with self.login(username=self.user1.username):
            self.post('fiction_outlines_api:arcnode_move', **self.good_move_data)
            self.response_200()
            assert self.node_to_test.path != ArcElementNode.objects.get(pk=self.node_to_test.pk).path


class ArcNodeCreateTest(ArcNodeAbstractTestCase):
    '''
    Tests for add_child and add_sibling via the API.
    '''

    def setUp(self):
        super().setUp()
        self.data = {
            'arc_element_type': 'beat',
            'description': 'This beat should be here.',
            'story_element_node': self.o1_valid_storynode.pk,
            'assoc_characters': [],
            'assoc_locations': [],
        }
        self.data_without_node = {
            'arc_element_type': 'beat',
            'description': 'This beat should be here.',
            'story_element_node': None,
            'assoc_characters': [],
            'assoc_locations': [],
        }
        self.bad_data_type = {
            'arc_element_type': 'mile_pt1',
            'description': 'An extra milestone too many.',
            'story_element_node': self.o1_valid_storynode.pk,
            'assoc_characters': [],
            'assoc_locations': [],
        }
        self.bad_data_node = {
            'arc_element_type': 'beat',
            'description': 'I am a beat.',
            'story_element_node': self.o1_invalid_node.pk,
            'assoc_characters': [],
            'assoc_locations': [],
        }
        self.url_kwargs = {
            'arcnode': self.node_to_test.pk,
            'action': 'add_child',
            'position': 'last-child',
            'extra': self.extra
        }
        self.bad_url_kwargs = {
            'arcnode': self.node_to_test.pk,
            'action': 'delete',
            'position': 'right',
            'extra': self.extra,

        }
        self.view_string = 'fiction_outlines_api:arcnode_create'
        self.before_create = ArcElementNode.objects.filter(arc=self.arc1).count()

    def test_login_required(self):
        '''
        You have to be logged in.
        '''
        self.post(self.view_string, data=self.data, **self.url_kwargs)
        self.response_403()
        assert ArcElementNode.objects.filter(arc=self.arc1).count() == self.before_create

    def test_object_permissions(self):
        '''
        Ensure that only an authorized user can create arc_nodes.
        '''
        for user in self.naughty_users:
            with self.login(username=user.username):
                self.post(self.view_string, data=self.data, **self.url_kwargs)
                self.response_403()
                assert ArcElementNode.objects.filter(arc=self.arc1).count() == self.before_create

    def test_invalid_submission(self):
        '''
        Test an invalid submission from an authorized user.
        '''
        with self.login(username=self.user1.username):
            self.post(self.view_string, data=self.bad_data_type, **self.url_kwargs)
            self.response_400()
            assert ArcElementNode.objects.filter(arc=self.arc1).count() == self.before_create
            self.post(self.view_string, data=self.bad_data_node, **self.url_kwargs)
            self.response_400()
            assert ArcElementNode.objects.filter(arc=self.arc1).count() == self.before_create

    def test_invalid_method(self):
        with self.login(username=self.user1.username):
            self.post(self.view_string, data=self.data, **self.bad_url_kwargs)
            self.response_404()
            assert ArcElementNode.objects.filter(arc=self.arc1).count() == self.before_create

    def test_invalid_positition_arg(self):
        with self.login(username=self.user1.username):
            self.bad_url_kwargs['position'] = 'over-there'
            self.bad_url_kwargs['action'] = 'add_sibling'
            self.post(self.view_string, data=self.data, **self.bad_url_kwargs)
            self.response_400()
            assert ArcElementNode.objects.filter(arc=self.arc1).count() == self.before_create

    def test_add_child_without_node(self):
        '''
        Test that an authorized user can create using a story node.
        '''
        with self.login(username=self.user1.username):
            self.post(self.view_string, data=self.data_without_node, **self.url_kwargs)
            self.response_201()
            assert ArcElementNode.objects.filter(arc=self.arc1).count() - self.before_create == 1

    def test_add_child_with_node(self):
        '''
        Test that an authorized user can execute add_child while specifiying a story node.
        '''
        with self.login(username=self.user1.username):
            self.post(self.view_string, data=self.data, **self.url_kwargs)
            self.response_201()
            assert ArcElementNode.objects.filter(arc=self.arc1).count() - self.before_create == 1

    def test_add_sibling_without_node(self):
        '''
        Test that an authorized user can add a node without a specifying a story node.
        '''
        self.url_kwargs['action'] = 'add_sibling'
        self.url_kwargs['position'] = 'right'
        with self.login(username=self.user1.username):
            self.post(self.view_string, data=self.data_without_node, **self.url_kwargs)
            self.response_201()
            assert ArcElementNode.objects.filter(arc=self.arc1).count() - self.before_create == 1

    def test_add_sibling_with_node(self):
        '''
        Test that user can create a sibling while also specifying the storynode.
        '''
        self.url_kwargs['action'] = 'add_sibling'
        self.url_kwargs['position'] = 'right'
        with self.login(username=self.user1.username):
            self.post(self.view_string, data=self.data, **self.url_kwargs)
            self.response_201()
            assert ArcElementNode.objects.filter(arc=self.arc1).count() - self.before_create == 1


# StoryNode Tests


class StoryNodeDetailTest(ArcNodeAbstractTestCase):
    '''
    Test cases for retrieving story node details.
    '''
    def setUp(self):
        super().setUp()
        self.view_string = 'fiction_outlines_api:storynode_item'
        self.url_kwargs = {
            'outline': self.o1.pk,
            'storynode': self.o1_valid_storynode.pk,
            'extra': self.extra,
        }

    def test_login_required(self):
        '''
        You have to be logged in.
        '''
        self.get(self.view_string, **self.url_kwargs)
        self.response_403()

    def test_object_permissions(self):
        '''
        Ensure that unauthorized users cannot access it.
        '''
        for user in self.naughty_users:
            with self.login(username=user.username):
                self.get(self.view_string, **self.url_kwargs)
                self.response_403()

    def test_authorized_user(self):
        with self.login(username=self.user1.username):
            self.get(self.view_string, **self.url_kwargs)
            self.response_200()
            assert StoryElementNodeSerializer(self.o1_valid_storynode).data == self.last_response.data


class StoryNodeDeleteTest(ArcNodeAbstractTestCase):
    '''
    Test cases for StoryNode deletion
    '''

    def setUp(self):
        super().setUp()
        self.view_string = 'fiction_outlines_api:storynode_item'
        self.url_kwargs = {
            'outline': self.o1.pk,
            'storynode': self.o1_valid_storynode.pk,
            'extra': self.extra
        }

    def test_login_required(self):
        '''
        You have to be logged in.
        '''
        self.delete(self.view_string, **self.url_kwargs)
        self.response_403()
        assert StoryElementNode.objects.get(pk=self.o1_valid_storynode.pk)

    def test_object_permissions(self):
        '''
        Ensure unauthorized users cannot delete.
        '''
        for user in self.naughty_users:
            with self.login(username=user.username):
                self.delete(self.view_string, **self.url_kwargs)
                self.response_403()
                assert StoryElementNode.objects.get(pk=self.o1_valid_storynode.pk)

    def test_authorized_user(self):
        '''
        Confirm that an authorized user can delete the object.
        '''
        with self.login(username=self.user1.username):
            self.delete(self.view_string, **self.url_kwargs)
            self.response_204()
            with pytest.raises(ObjectDoesNotExist):
                StoryElementNode.objects.get(pk=self.o1_valid_storynode.pk)


class StoryNodeUpdateTest(ArcNodeAbstractTestCase):
    '''
    Tests for updating story node objects.
    '''

    def setUp(self):
        super().setUp()
        self.view_string = 'fiction_outlines_api:storynode_item'
        self.url_kwargs = {
            'outline': self.o1.pk,
            'storynode': self.o1_valid_storynode.pk,
            'extra': self.extra,
        }
        self.long_data = {
            'story_element_type': 'chapter',
            'name': 'Chapter 1',
            'description': 'Updating the description',
            'assoc_characters': [self.c1int.pk],
            'assoc_locations': [self.l1int.pk],
        }
        self.bad_data_wrong_character = {
            'story_element_type': 'chapter',
            'name': 'Chapter 1',
            'description': 'Updating the description',
            'assoc_characters': [self.c3int.pk],
            'assoc_locations': [self.l1int.pk],
        }
        self.bad_data_wrong_location = {
            'story_element_type': 'chapter',
            'name': 'Chapter 1',
            'description': 'Updating the description',
            'assoc_characters': [self.c1int.pk],
            'assoc_locations': [self.l1int2.pk],
        }
        self.bad_data_wrong_type = {
            'story_element_type': 'part',
            'name': 'Chapter 1',
            'description': 'Updating the description',
            'assoc_characters': [self.c1int.pk],
            'assoc_locations': [self.l1int.pk],
        }
        self.short_data = {
            'name': "Chapter One"
        }

    def test_login_required(self):
        '''
        You have to be logged in.
        '''
        self.put(self.view_string, data=self.long_data, **self.url_kwargs)
        self.response_403()
        node_check = StoryElementNode.objects.get(pk=self.o1_valid_storynode.pk)
        assert node_check.description == self.o1_valid_storynode.description
        assert node_check.assoc_characters.count() == self.o1_valid_storynode.assoc_characters.count()
        assert node_check.assoc_locations.count() == self.o1_valid_storynode.assoc_locations.count()
        self.patch(self.view_string, data=self.short_data, **self.url_kwargs)
        self.response_403()
        assert StoryElementNode.objects.get(pk=self.o1_valid_storynode.pk).name == self.o1_valid_storynode.name

    def test_object_permissions(self):
        '''
        Ensure unauthorized users cannot edit the object.
        '''
        for user in self.naughty_users:
            with self.login(username=user.username):
                self.put(self.view_string, data=self.long_data, **self.url_kwargs)
                self.response_403()
                node_check = StoryElementNode.objects.get(pk=self.o1_valid_storynode.pk)
                assert node_check.description == self.o1_valid_storynode.description
                assert node_check.assoc_characters.count() == self.o1_valid_storynode.assoc_characters.count()
                assert node_check.assoc_locations.count() == self.o1_valid_storynode.assoc_locations.count()
                self.patch(self.view_string, data=self.short_data, **self.url_kwargs)
                self.response_403()
                assert StoryElementNode.objects.get(pk=self.o1_valid_storynode.pk).name == self.o1_valid_storynode.name

    def test_invalid_character(self):
        '''
        Ensure authorized users can't associate an invalid character instance.
        '''
        with self.login(username=self.user1.username):
            self.put(self.view_string, data=self.bad_data_wrong_character, **self.url_kwargs)
            self.response_400()
            node_check = StoryElementNode.objects.get(pk=self.o1_valid_storynode.pk)
            assert node_check.description == self.o1_valid_storynode.description
            assert node_check.assoc_characters.count() == self.o1_valid_storynode.assoc_characters.count()
            assert node_check.assoc_locations.count() == self.o1_valid_storynode.assoc_locations.count()

    def test_invalid_location(self):
        '''
        Ensure authorized user cannot associate an invalid location instance.
        '''
        with self.login(username=self.user1.username):
            self.put(self.view_string, data=self.bad_data_wrong_location, **self.url_kwargs)
            self.response_400()
            node_check = StoryElementNode.objects.get(pk=self.o1_valid_storynode.pk)
            assert node_check.description == self.o1_valid_storynode.description
            assert node_check.assoc_characters.count() == self.o1_valid_storynode.assoc_characters.count()
            assert node_check.assoc_locations.count() == self.o1_valid_storynode.assoc_locations.count()

    def test_invalid_type(self):
        '''
        Ensure authorized user cannot edit the record to an invalid story element type.
        '''
        with self.login(username=self.user1.username):
            self.put(self.view_string, data=self.bad_data_wrong_type, **self.url_kwargs)
            self.response_400()
            node_check = StoryElementNode.objects.get(pk=self.o1_valid_storynode.pk)
            assert node_check.description == self.o1_valid_storynode.description
            assert node_check.assoc_characters.count() == self.o1_valid_storynode.assoc_characters.count()
            assert node_check.assoc_locations.count() == self.o1_valid_storynode.assoc_locations.count()
            assert node_check.story_element_type == self.o1_valid_storynode.story_element_type

    def test_valid_submissions(self):
        '''
        Test that valid submissions update as expected.
        '''
        with self.login(username=self.user1.username):
            self.patch(self.view_string, data=self.short_data, **self.url_kwargs)
            self.response_200()
            assert StoryElementNode.objects.get(pk=self.o1_valid_storynode.pk).name == 'Chapter One'
            self.put(self.view_string, data=self.long_data, **self.url_kwargs)
            self.response_200()
            node_check = StoryElementNode.objects.get(pk=self.o1_valid_storynode.pk)
            assert node_check.description != self.o1_valid_storynode.description
            assert node_check.assoc_characters.count() == 1
            assert node_check.assoc_locations.count() == 1


class StoryNodeMoveTest(ArcNodeAbstractTestCase):
    '''
    Tests for moving storynode objects.
    '''

    def setUp(self):
        super().setUp()
        self.o1_scene1 = self.o1_valid_storynode.add_child(story_element_type='ss', name='Staring in a mirror',
                                                           description='describe the protagonist')
        self.o1_valid_storynode.refresh_from_db()
        self.o1_scene2 = self.o1_valid_storynode.add_child(story_element_type='ss',
                                                           name='walk and talk',
                                                           description='copy and paste, find and replace.')
        self.o1_valid_storynode.refresh_from_db()
        self.o1_chap2 = self.part1.add_child(story_element_type='chapter', name='chapter2',
                                             description="I have no idea what I'm doing")
        self.part1.refresh_from_db()
        self.view_string = 'fiction_outlines_api:storynode_move'
        self.valid_url_kwargs = {
            'node_to_move_id': self.o1_valid_storynode.pk,
            'target_node_id': self.o1_valid_storynode.get_next_sibling().pk,
            'position': 'right',
        }
        self.invalid_url_kwargs_root = {
            'node_to_move_id': self.o1_valid_storynode.pk,
            'target_node_id': self.o1_valid_storynode.get_root().pk,
            'position': 'right'
        }
        self.invalid_url_kwargs_descendant = {
            'node_to_move_id': self.o1_valid_storynode.pk,
            'target_node_id': self.o1_scene1.pk,
            'position': 'right',
        }
        self.invalid_url_kwargs_structure = {
            'node_to_move_id': self.o1_valid_storynode.pk,
            'target_node_id': self.o1_chap2.pk,
            'position': 'first-child',
        }
        self.invalid_url_kwargs_outline = {
            'node_to_move_id': self.o1_valid_storynode.pk,
            'target_node_id': self.o1_invalid_node.pk,
            'position': 'right',
        }

    def test_login_required(self):
        '''
        You have to be logged in.
        '''
        self.post(self.view_string, **self.valid_url_kwargs)
        self.response_403()
        assert StoryElementNode.objects.get(pk=self.o1_valid_storynode.pk).path == self.o1_valid_storynode.path

    def test_object_permissions(self):
        '''
        Ensure that unauthorized users cannot move the node.
        '''
        for user in self.naughty_users:
            with self.login(username=user.username):
                self.post(self.view_string, **self.valid_url_kwargs)
                self.response_403()
                assert StoryElementNode.objects.get(pk=self.o1_valid_storynode.pk).path == self.o1_valid_storynode.path

    def test_invalid_move_root(self):
        '''
        Prevent moving a storynode to the root level.
        '''
        with self.login(username=self.user1.username):
            self.post(self.view_string, **self.invalid_url_kwargs_root)
            self.response_400()
            assert StoryElementNode.objects.get(pk=self.o1_valid_storynode.pk).path == self.o1_valid_storynode.path

    def test_invalid_move_descendant(self):
        '''
        Prevent moving a storynode in relation to its descendant
        '''
        with self.login(username=self.user1.username):
            self.post(self.view_string, **self.invalid_url_kwargs_descendant)
            self.response_400()
            assert StoryElementNode.objects.get(pk=self.o1_valid_storynode.pk).path == self.o1_valid_storynode.path

    def test_invalid_move_structure(self):
        '''
        Prevent a move that violates the outline structure
        '''
        with self.login(username=self.user1.username):
            self.post(self.view_string, **self.invalid_url_kwargs_structure)
            self.response_400()
            assert StoryElementNode.objects.get(pk=self.o1_valid_storynode.pk).path == self.o1_valid_storynode.path

    def test_invalid_move_to_other_outline(self):
        '''
        Prevent a storynode from being moved to a different outline.
        '''
        with self.login(username=self.user1.username):
            self.post(self.view_string, **self.invalid_url_kwargs_outline)
            self.response_400()
            assert StoryElementNode.objects.get(pk=self.o1_valid_storynode.pk).path == self.o1_valid_storynode.path

    def test_valid_move(self):
        '''
        Test that authorized user can make a valid move.
        '''
        with self.login(username=self.user1.username):
            self.post(self.view_string, **self.valid_url_kwargs)
            self.response_200()
            assert StoryElementNode.objects.get(pk=self.o1_valid_storynode.pk).path != self.o1_valid_storynode.path


class StoryNodeCreateTest(ArcNodeAbstractTestCase):
    '''
    Tests for StoryNode creation views
    '''
    def setUp(self):
        super().setUp()
        self.view_string = 'fiction_outlines_api:storynode_create'
        self.child_url_kwargs = {
            'storynode': self.o1_valid_storynode.pk,
            'action': 'add_child',
            'position': None,
        }
        self.sibling_url_kwargs = {
            'storynode': self.o1_valid_storynode.pk,
            'action': 'add_sibling',
            'position': 'right',
        }
        self.bad_data_part = {
            'story_element_type': 'part',
            'name': 'bad part',
            'description': 'In this scene, our hero must play host to sloths.'
        }
        self.data_scene = {
            'story_element_type': 'ss',
            'name': 'unexpected_party',
            'description': 'In this scene, our hero must play host to sloths.',
        }
        self.data_followup = {
            'story_element_type': 'chapter',
            'name': 'Cleaning up',
            'description': 'In this chapter, our hero must pick up sloth feces.'
        }

    def test_login_required(self):
        '''
        You have to be logged in.
        '''
        self.post(self.view_string, data=self.data_scene, **self.child_url_kwargs)
        self.response_403()
        self.o1_valid_storynode.refresh_from_db()
        assert not self.o1_valid_storynode.get_children()

    def test_object_permissions(self):
        '''
        Ensure that unauthorized users cannot add an object.
        '''
        for user in self.naughty_users:
            with self.login(username=user.username):
                self.post(self.view_string, data=self.data_scene, **self.child_url_kwargs)
                self.response_403()
                self.o1_valid_storynode.refresh_from_db()
                assert not self.o1_valid_storynode.get_children()

    def test_invalid_submission_for_outline_structure(self):
        '''
        Ensure that the allowed parent/child rules are honored.
        '''
        with self.login(username=self.user1.username):
            self.post(self.view_string, data=self.bad_data_part, **self.child_url_kwargs)
            self.response_400()
            self.o1_valid_storynode.refresh_from_db()
            assert not self.o1_valid_storynode.get_children()

    def test_valid_submissions(self):
        '''
        Test that authorized user can create normally.
        '''
        with self.login(username=self.user1.username):
            self.post(self.view_string, data=self.data_scene, **self.child_url_kwargs)
            self.response_201()
            self.o1_valid_storynode.refresh_from_db()
            assert len(self.o1_valid_storynode.get_children()) == 1
            self.post(self.view_string, data=self.data_followup, **self.sibling_url_kwargs)
            self.response_201()
            self.o1_valid_storynode.refresh_from_db()
            assert self.o1_valid_storynode.get_next_sibling().name == 'Cleaning up'
