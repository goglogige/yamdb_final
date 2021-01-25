from rest_framework import serializers

from .models import Category, Comment, Genre, Review, Title, User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id', 'first_name', 'last_name', 'username',
            'bio', 'email', 'role',
        )


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=75, required=True)


class EmailCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=75, required=True)
    confirmation_code = serializers.CharField(
        max_length=2000,
        required=True
    )


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Genre


class TitlePostSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        many=True,
        queryset=Genre.objects.all())
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all())

    class Meta:
        model = Title
        fields = '__all__'


class TitleListSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.FloatField()

    class Meta:
        model = Title
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    def validate(self, attrs):
        author = self.context["request"].user.id,
        title = self.context["view"].kwargs.get("title_id")
        message = 'Author review already exist'
        if not self.instance and Review.objects.filter(
                title=title,
                author=author
        ).exists():
            raise serializers.ValidationError(message)
        return attrs

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
