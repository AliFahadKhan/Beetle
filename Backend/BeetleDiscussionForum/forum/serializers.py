from rest_framework_mongoengine.serializers import DocumentSerializer, EmbeddedDocumentSerializer
from forum.models import Forum, Comment, CommentReport

class CommentSerializer(EmbeddedDocumentSerializer):
    class Meta:
        model= Comment
        fields = ('comment_id','creator_id', 'creator_name','text', 'voice_note', 'image', 'date_created')

class CommentReportSerializer(DocumentSerializer):
    class Meta:
        model = CommentReport

class ForumsSerializer(DocumentSerializer):
    class Meta:
        model = Forum
        fields = ('id', 'author_id', 'author_name' ,'title', 'description', 'image')
        depth = 2

class ForumSerializer(DocumentSerializer):
    comments = CommentSerializer(many=True)
    class Meta:
        model = Forum
        fields = ('id', 'author_id', 'author_name' ,'title', 'description', 'image', 'comments', 'date_created')
        depth = 2
    
    def update(self, instance, validated_data):
        comments = validated_data.pop('comments')
        updated_instance = super(ForumSerializer, self).update(instance, validated_data)

        for comment_data in comments:
            updated_instance.comments.append(Comment(**comment_data))
        
        updated_instance.save()
        return updated_instance
    
    def create(self, validated_data):
        comments = validated_data.pop("comments")
        forum = Forum.objects.create(**validated_data)
        forum.comments = []

        for comment in comments:
            forum.comments.append(Comment(**comment))

        forum.save()
        return forum