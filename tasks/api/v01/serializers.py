from rest_framework import serializers

from tasks.models import Category, Task
from accounts.models import Profile

## Create your serializers here
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class TaskSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(read_only=True, slug_field='profile_user__username')
    category = serializers.SlugRelatedField(slug_field='name', queryset=Category.objects.all())
    class Meta:
        model = Task
        fields = ['id', 'author', 'title', 'status', 'category', 'importance', 'created_date',
                  'edited_date', 'completed_date']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            profile_determine = Profile.objects.get(profile_user=request.user)
            self.fields['category'].queryset = Category.objects.filter(creator=profile_determine)

    def create(self, validated_data):
        validated_data['author'] = Profile.objects.get(profile_user=self.context.get('request').user)
        return super().create(validated_data)
    
    def to_representation(self, instance):
        request = self.context.get('request')
        rep = super().to_representation(instance)
        print(type(request.parser_context))
        print(request.parser_context.get('kwargs'))
        if not request.parser_context.get('kwargs').get('pk'):
            rep.pop('created_date')
            rep.pop('edited_date')
            rep.pop('completed_date')
        return rep

    