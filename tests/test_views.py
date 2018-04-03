from test_plus import APITestCase
from fiction_outlines.models import Series, Character, Location, Outline
from fiction_outlines.models import Arc, ArcElementNode, StoryElementNode
from fiction_outlines.models import CharacterInstance, LocationInstance
from fiction_outlines_api.serializers import SeriesSerializer


class FictionOutlineAbstractTestCase(APITestCase):
    '''
    An abstract class to make test setup less repetitive.
    '''

    def setUp(self):
        '''
        Generic data setup for test cases.
        '''
        self.user1 = self.make_user('u1')
        self.user2 = self.make_user('u2')
        self.user3 = self.make_user('u3')
        self.s1 = Series(title='Urban Fantasy Series', user=self.user1)
        self.s1.save()
        self.s2 = Series(title='Space Opera Trilogy', user=self.user1)
        self.s2.save()
        self.s3 = Series(title='Mil-SF series', user=self.user2)
        self.s3.save()
        self.c1 = Character(name='John Doe', tags='ptsd, anxiety', user=self.user1)
        self.c2 = Character(name='Jane Doe', tags='teen, magical', user=self.user1)
        self.c1.save()
        self.c2.save()
        self.c1.series.add(self.s1)
        self.c2.series.add(self.s2)
        self.c3 = Character(name='Michael Smith', user=self.user2)
        self.c4 = Character(name='Eliza Doolittle', tags='muderess', user=self.user2)
        self.c3.save()
        self.c3.series.add(self.s3)
        self.c4.save()
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
