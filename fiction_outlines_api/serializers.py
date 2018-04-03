from rest_framework import serializers
from taggit_serializer.serializers import TaggitSerializer, TagListSerializerField
from fiction_outlines.models import Series, Character, Location, Outline
from fiction_outlines.models import CharacterInstance, LocationInstance, Arc
from fiction_outlines.models import ArcElementNode, StoryElementNode


class SeriesSerializer(TaggitSerializer, serializers.ModelSerializer):
    '''
    Serializer for Series model.
    '''

    tags = TagListSerializerField()

    class Meta:
        model = Series
        fields = ('id', 'title', 'description', 'tags')


class CharacterSerializer(TaggitSerializer, serializers.ModelSerializer):
    '''
    Serializer for Character model.
    '''

    tags = TagListSerializerField()

    class Meta:
        model = Character
        fields = ('id', 'name', 'description', 'series', 'tags')


class LocationSerializer(TaggitSerializer, serializers.ModelSerializer):
    '''
    Serializer for Location model.
    '''

    tags = TagListSerializerField()

    class Meta:
        model = Location
        fields = ('id', 'name', 'description', 'series', 'tags')


class OutlineSerializer(TaggitSerializer, serializers.ModelSerializer):
    '''
    Serializer for Outline model.
    '''

    tags = TagListSerializerField()

    class Meta:
        model = Outline
        fields = ('id', 'title', 'description', 'series', 'tags')


class ArcSerializer(serializers.ModelSerializer):
    '''
    Serializer for Arc model.
    '''
    class Meta:
        model = Arc
        fields = ('id', 'name', 'mace_type', 'outline')


class CharacterInstanceSerializer(serializers.ModelSerializer):
    '''
    Serializer for character instance.
    '''
    class Meta:
        model = CharacterInstance
        fields = ('id', 'outline', 'character', 'main_character', 'pov_character', 'protagonist',
                  'antagonist', 'obstacle', 'villain')


class LocationInstanceSerializer(serializers.ModelSerializer):
    '''
    Serializer for location instance.
    '''
    class Meta:
        model = LocationInstance
        fields = ('id', 'location', 'outline')


class ArcElementNodeSerializer(serializers.ModelSerializer):
    '''
    Serializer for ArcElementNode
    '''
    class Meta:
        model = ArcElementNode
        fields = ('id', 'arc', 'arc_element_type', 'headline', 'description', 'story_element_node',
                  'assoc_characters', 'assoc_locations')


class StoryElementNodeSerializer(serializers.ModelSerializer):
    '''
    Serializer for StoryElementNode
    '''
    class Meta:
        model = StoryElementNode
        fields = ('id', 'name', 'description', 'outline', 'assoc_characters', 'assoc_locations')
