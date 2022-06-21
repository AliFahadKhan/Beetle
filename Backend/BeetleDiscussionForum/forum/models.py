from datetime import datetime
from mongoengine import Document, EmbeddedDocument, connect, LongField, StringField, FileField, ObjectIdField, EmbeddedDocumentListField, DateTimeField


connect( db="ali-db", username="Beetle", password="cBctbaMZIcarfP33", host="mongodb+srv://Beetle:cBctbaMZIcarfP33@cluster0.ajmpj.mongodb.net/ali_db?retryWrites=true&w=majority")

class Comment(EmbeddedDocument):
    comment_id = ObjectIdField()
    creator_id = LongField(default=0, required=True)
    creator_name = StringField(default="", required=True)
    text = StringField(default="")
    voice_note = FileField()
    image = FileField()
    date_created = DateTimeField(default=datetime.utcnow)

class Forum(Document):
    author_id=LongField(default=0, required=True)
    author_name=StringField(default="", required=True) 
    title=StringField(default="")
    description=StringField()
    image=FileField()
    comments = EmbeddedDocumentListField(Comment)
    date_created = DateTimeField(default=datetime.utcnow)

class CommentReport(Document):
    user_id = LongField(default=0, required=True)
    comment_id = ObjectIdField(default=0, required=True)