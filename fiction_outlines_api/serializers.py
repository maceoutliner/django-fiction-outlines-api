from rest_framework import serializers
from taggit_serializer.serializers import TaggitSerializer, TagListSerializerField
from fiction_outlines.models import Series, Character, Location, Outline
from fiction_outlines.models import CharacterInstance, LocationInstance, Arc
from fiction_outlines.models import ArcElementNode, StoryElementNode, MACE_TYPES


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
    series = serializers.PrimaryKeyRelatedField(many=True, allow_null=True, queryset=Series.objects.all())

    class Meta:
        model = Character
        fields = ('id', 'name', 'description', 'series', 'tags')


class LocationSerializer(TaggitSerializer, serializers.ModelSerializer):
    '''
    Serializer for Location model.
    '''

    tags = TagListSerializerField()
    series = serializers.PrimaryKeyRelatedField(many=True, allow_null=True, queryset=Series.objects.all())

    class Meta:
        model = Location
        fields = ('id', 'name', 'description', 'series', 'tags')


class OutlineSerializer(TaggitSerializer, serializers.ModelSerializer):
    '''
    Serializer for Outline model.
    '''

    length_estimate = serializers.IntegerField(read_only=True, required=False)
    tags = TagListSerializerField()
    series = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Series.objects.all())
    arc_set = serializers.PrimaryKeyRelatedField(many=True, required=False, read_only=True)
    characterinstance_set = serializers.PrimaryKeyRelatedField(many=True, required=False, read_only=True)
    locationinstance_set = serializers.PrimaryKeyRelatedField(many=True, required=False, read_only=True)

    class Meta:
        model = Outline
        fields = ('id', 'title', 'description', 'series', 'tags', 'length_estimate', 'arc_set',
                  'characterinstance_set', 'locationinstance_set')


class ArcSerializer(serializers.ModelSerializer):
    '''
    Serializer for Arc model.
    '''

    outline = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
    current_errors = serializers.ReadOnlyField(read_only=True, required=False)

    class Meta:
        model = Arc
        fields = ('id', 'name', 'mace_type', 'outline', 'current_errors')


class ArcCreateSerializer(serializers.Serializer):
    '''
    Serializer used for arc creation.
    '''
    mace_type = serializers.ChoiceField(choices=MACE_TYPES)
    name = serializers.CharField(max_length=255)


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
