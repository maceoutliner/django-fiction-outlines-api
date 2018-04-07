import logging
from rest_framework import serializers
from taggit_serializer.serializers import TaggitSerializer, TagListSerializerField
from fiction_outlines.models import Series, Character, Location, Outline
from fiction_outlines.models import CharacterInstance, LocationInstance, Arc
from fiction_outlines.models import ArcElementNode, StoryElementNode, MACE_TYPES


logger = logging.getLogger('fiction-outlines-api')

MOVE_POSITION_CHOICES = (
    ('first-child', 'first-child'),
    ('last-child', 'last-child'),
    ('first-sibling', 'first-sibling'),
    ('last-sibling', 'last-sibling'),
    ('left', 'left'),
    ('right', 'right'),
)


def convert_annotated_list(annotated_list, serializer_class):
    converted_list = []  # pragma: no cover
    for item, info in annotated_list:
        converted_list.append((serializer_class(item).data, info))
    return converted_list


class SeriesSerializer(TaggitSerializer, serializers.ModelSerializer):
    '''
    Serializer for Series model.
    '''

    tags = TagListSerializerField()

    class Meta:  # pragma: no cover
        model = Series
        fields = ('id', 'title', 'description', 'tags')


class CharacterInstanceSerializer(serializers.ModelSerializer):
    '''
    Serializer for character instance.
    '''
    name = serializers.CharField(read_only=True, source='character.name')

    class Meta:  # pragma: no cover
        model = CharacterInstance
        fields = ('id', 'outline', 'character', 'name', 'main_character', 'pov_character', 'protagonist',
                  'antagonist', 'obstacle', 'villain')
        read_only_fields = ('id', 'outline', 'character', 'name')
        extra_kwargs = {}
        for field in read_only_fields:
            extra_kwargs['field'] = {'required': False}


class LocationInstanceSerializer(serializers.ModelSerializer):
    '''
    Serializer for location instance.
    '''
    name = serializers.CharField(read_only=True, source='location.name')

    class Meta:  # pragma: no cover
        model = LocationInstance
        fields = ('id', 'location', 'name', 'outline')
        read_only_fields = ('id', 'location', 'name', 'outline')
        extra_kwargs = {}
        for field in read_only_fields:
            extra_kwargs['field'] = {'required': False}


class CharacterSerializer(TaggitSerializer, serializers.ModelSerializer):
    '''
    Serializer for Character model.
    '''

    tags = TagListSerializerField()
    series = serializers.PrimaryKeyRelatedField(many=True, allow_null=True, queryset=Series.objects.all())
    character_instances = CharacterInstanceSerializer(many=True, read_only=True,
                                                      required=False, source='characterinstance_set')

    class Meta:  # pragma: no cover
        model = Character
        fields = ('id', 'name', 'description', 'series', 'tags', 'character_instances')


class LocationSerializer(TaggitSerializer, serializers.ModelSerializer):
    '''
    Serializer for Location model.
    '''

    tags = TagListSerializerField()
    series = serializers.PrimaryKeyRelatedField(many=True, allow_null=True, queryset=Series.objects.all())
    location_instances = LocationInstanceSerializer(many=True, read_only=True,
                                                    required=False, source='locationinstance_set')

    class Meta:  # pragma: no cover
        model = Location
        fields = ('id', 'name', 'description', 'series', 'tags', 'location_instances')


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
    outline_structure = serializers.SerializerMethodField(read_only=True)

    def get_outline_structure(self, obj):
        logger.debug("Checking outline structure.")
        if obj.story_tree_root:
            logger.debug('Found a root node')
            annotated_list = StoryElementNode.get_annotated_list(obj.story_tree_root)
            logger.debug('Annotated list retrieved.')
            if len(annotated_list) > 1:
                # There is more than just a single root node: serialize and return.
                annotated_list = convert_annotated_list(annotated_list, StoryElementNodeSerializer)
                logger.debug("Returning results to field.")  # pragma: no cover
                return annotated_list[1:]
        return []

    class Meta:  # pragma: no cover
        model = Outline
        fields = ('id', 'title', 'description', 'series', 'tags', 'length_estimate', 'arc_set',
                  'characterinstance_set', 'locationinstance_set', 'outline_structure')


class ArcSerializer(serializers.ModelSerializer):
    '''
    Serializer for Arc model.
    '''

    outline = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
    current_errors = serializers.ReadOnlyField(read_only=True, required=False)
    arc_structure = serializers.SerializerMethodField(read_only=True)

    def get_arc_structure(self, obj):
        logger.debug("Attempting to retrieve arc structure for arc %s" % obj.pk)
        if obj.arc_root_node:
            annotated_list = ArcElementNode.get_annotated_list(obj.arc_root_node)
            logger.debug("Retrieved annotated list")
            if len(annotated_list) > 1:
                # There is more than just a root node which we don't want to display to users.
                logger.debug("Arc structure found, builidng serialized structure.")
                annotated_list = convert_annotated_list(annotated_list, ArcElementNodeSerializer)
                logger.debug("Success serializing arc!")
                logger.debug("Arc looks like this:\n\n%s" % annotated_list[1:])
                logger.debug("Returning result to field.")
                return annotated_list[1:]
            else:
                logger.debug("Only a root node... returning empty list.")
        return []  # pragma: no cover This is really unlikely to occur.

    class Meta:  # pragma: no cover
        model = Arc
        fields = ('id', 'name', 'mace_type', 'outline', 'current_errors', 'arc_structure')


class ArcCreateSerializer(serializers.Serializer):
    '''
    Serializer used for arc creation.
    '''
    mace_type = serializers.ChoiceField(choices=MACE_TYPES)
    name = serializers.CharField(max_length=255)


class ArcElementNodeSerializer(serializers.ModelSerializer):
    '''
    Serializer for ArcElementNode
    '''

    arc = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
    headline = serializers.ReadOnlyField(required=False)
    story_element_node = serializers.PrimaryKeyRelatedField(required=False, allow_null=True,
                                                            queryset=StoryElementNode.objects.all())
    parent_outline = serializers.PrimaryKeyRelatedField(source='arc.outline', read_only=True, required=False)
    milestone_seq = serializers.IntegerField(allow_null=True, read_only=True, required=False)

    class Meta:  # pragma: no cover
        model = ArcElementNode
        fields = ('id', 'arc', 'arc_element_type', 'headline', 'description', 'story_element_node',
                  'assoc_characters', 'assoc_locations', 'milestone_seq', 'is_milestone', 'parent_outline')


class StoryElementNodeSerializer(serializers.ModelSerializer):
    '''
    Serializer for StoryElementNode
    '''

    all_characters = CharacterInstanceSerializer(many=True, read_only=True, required=False)
    all_locations = LocationInstanceSerializer(many=True, read_only=True, required=False)
    outline = serializers.PrimaryKeyRelatedField(read_only=True, required=False)

    class Meta:  # pragma: no cover
        model = StoryElementNode
        fields = ('id', 'story_element_type', 'name', 'description', 'outline', 'assoc_characters',
                  'assoc_locations', 'all_characters', 'all_locations', 'impact_rating')
        read_only_fields = ('all_characters', 'all_locations', 'impact_rating', 'outline', 'id')
