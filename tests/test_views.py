import logging
import pytest
from django.core.exceptions import ObjectDoesNotExist
from test_plus import APITestCase
from fiction_outlines.models import Series, Character, Location, Outline, Arc
# from fiction_outlines.models import Arc, ArcElementNode, StoryElementNode
from fiction_outlines.models import CharacterInstance, LocationInstance
from fiction_outlines_api.serializers import SeriesSerializer, CharacterSerializer, LocationSerializer
from fiction_outlines_api.serializers import OutlineSerializer, ArcSerializer

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
        for user in [self.user2, self.user3]:
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
        for user in [self.user2, self.user3]:
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
        for user in [self.user2, self.user3]:
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
        for user in [self.user2, self.user3]:
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
        for user in [self.user2, self.user3]:
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
        for user in [self.user2, self.user3]:
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
        for user in [self.user2, self.user3]:
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
        for user in [self.user2, self.user3]:
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
        for user in [self.user2, self.user3]:
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
        for user in [self.user2, self.user3]:
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
        for user in [self.user2, self.user3]:
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
        for user in [self.user2, self.user3]:
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
        for user in [self.user2, self.user3]:
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
        for user in [self.user2, self.user3]:
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
        for user in [self.user2, self.user3]:
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
        for user in [self.user2, self.user3]:
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
