from django.http.response import JsonResponse
from django.contrib.auth.models import User
from django.core.files.base import ContentFile

from forum.models import Forum
from forum.models import Comment as comment
from forum.serializers import ForumsSerializer, ForumSerializer, CommentSerializer, CommentReportSerializer

from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from mongoengine.connection import get_db
import gridfs
import base64
from bson import ObjectId


db= get_db()
fs = gridfs.GridFS(db)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def forums_api(request):
    if request.method=="POST":
        Forum_data=JSONParser().parse(request)

        req_auth_info = request.headers.get('Authorization')
        auth_info=base64.b64decode(req_auth_info[6:]).decode()
        auth_info=auth_info.split(":")
        req_user = User.objects.get(username=auth_info[0])
        Forum_data["author_id"] = req_user.pk
        Forum_data["author_name"] = req_user.first_name + " " +req_user.last_name
       
        if 'image' in Forum_data.keys():
            decode = base64.b64decode(Forum_data["image"])
            file = ContentFile(decode, name="image.png")
            Forum_data["image"] = file
        Forum_serializer = ForumSerializer(data=Forum_data)
        if Forum_serializer.is_valid():
            Forum_serializer.save()
            return JsonResponse("Added Successfully",safe=False, status=status.HTTP_201_CREATED) 
        return JsonResponse(Forum_serializer.errors,safe=False, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method=="GET":
        search = request.GET.get('search','')
        order = request.GET.get('order','')

        if order == 'desc':
            order_query = '+'
        else:
            order_query = '-'

        if search != '':
            forums = Forum.objects(title__icontains=search).exclude('comments').order_by(order_query + 'date_created')

        else:
            forums = Forum.objects.all().exclude("comments").order_by(order_query + 'date_created')
        
        if(not forums):
            return JsonResponse({'message' : 'No forum found'}, status=status.HTTP_404_NOT_FOUND)
            
        forums_serializer = ForumsSerializer(forums, many=True)
        return JsonResponse(forums_serializer.data, safe=False)

@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def forum_api(request, forum_id):
    try:
        forum = Forum.objects(id=forum_id).get()
    except:
        return JsonResponse({'message': 'The Forum does not exist'}, status=status.HTTP_404_NOT_FOUND)
    if request.method == "GET":
        forums_serializer = ForumSerializer(forum)
        return JsonResponse(forums_serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == "DELETE":
        req_auth_info = request.headers.get('Authorization')
        auth_info=base64.b64decode(req_auth_info[6:]).decode()
        auth_info=auth_info.split(":")
        req_user = User.objects.get(username=auth_info[0])

        if (forum.author_id != req_user.pk):
            return JsonResponse({"Message" : "Unauthorized Operation"}, status=status.HTTP_403_FORBIDDEN, safe=False)

        forum.delete()
        return JsonResponse({"Message" : "Forum deleted successfully"}, status=status.HTTP_200_OK, safe=False)

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def image_api(request, file_id):
    oid = ObjectId(file_id)
    img=base64.b64encode(fs.get(oid).read()).decode('utf-8')
    return JsonResponse({"image_id": file_id, "image": img})

@api_view(['POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def comments_api(request, forum_id):
    try:
        forum = Forum.objects(id=forum_id).get()
    except:
        return JsonResponse({'message': 'The Forum does not exist'}, status=status.HTTP_404_NOT_FOUND)
    comment_data = JSONParser().parse(request)

    req_auth_info = request.headers.get('Authorization')
    auth_info=base64.b64decode(req_auth_info[6:]).decode()
    auth_info=auth_info.split(":")
    req_user = User.objects.get(username=auth_info[0])
    comment_data["creator_name"]=req_user.first_name + " " + req_user.last_name
    comment_data["creator_id"]=req_user.pk
    comment_data["comment_id"]=ObjectId()

    if 'image' in comment_data.keys():
        decode = base64.b64decode(comment_data["image"])
        file = ContentFile(decode, name="image1.png")
        comment_data["image"] = file
    
    if 'voice_note' in comment_data.keys():
        decode = base64.b64decode(comment_data["voice_note"])
        file = ContentFile(decode, name="image1.png")
        comment_data["voice_note"] = file
    
    comment_serializer = CommentSerializer(data=comment_data)
    if comment_serializer.is_valid():
        forum.comments.insert(0,comment(**comment_serializer.validated_data))
        forum.save()
        return JsonResponse({"Message" : "Added"}, status=status.HTTP_201_CREATED, safe=False)
    return JsonResponse(comment_serializer.errors, safe=False, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def comment_api(request, forum_id, comment_id):
    forum = Forum.objects(id=forum_id).get()
    if(not forum):
        return JsonResponse({'message': 'The Forum does not exist'}, status=status.HTTP_404_NOT_FOUND)
    comment = forum.comments.filter(comment_id=comment_id)
    if(not comment):
        return JsonResponse({'message': 'The comment does not exist'}, status=status.HTTP_404_NOT_FOUND)
    
    req_auth_info = request.headers.get('Authorization')
    auth_info=base64.b64decode(req_auth_info[6:]).decode()
    auth_info=auth_info.split(":")
    req_user = User.objects.get(username=auth_info[0])

    if (comment.get()["creator_id"] != req_user.pk):
        return JsonResponse({"Message" : "Unauthorized Operation"}, status=status.HTTP_403_FORBIDDEN, safe=False)

    if request.method == "DELETE":
        comment.delete()
        forum.save()
        return JsonResponse({"Message" : "Comment deleted successfully"}, status=status.HTTP_200_OK, safe=False)

    elif request.method == "PUT":
        comment_data = JSONParser().parse(request)
        if 'image' in comment_data.keys():
            decode = base64.b64decode(comment_data["image"])
            file = ContentFile(decode, name="image1.png")
            comment_data["image"] = file
    
        if 'voice_note' in comment_data.keys():
            decode = base64.b64decode(comment_data["voice_note"])
            file = ContentFile(decode, name="image1.png")
            comment_data["voice_note"] = file
        
        comment_serializer = CommentSerializer(data=comment_data)
        if comment_serializer.is_valid():
            if "image" in comment_serializer.validated_data.keys():
                curr_image_id = comment.get()["image"]
                if curr_image_id:
                    gridfs.GridFS(db, collection='comments').delete(ObjectId(curr_image_id.grid_id))
            if "voice_note" in comment_serializer.validated_data.keys():
                curr_voice_id = comment.get()["voice_note"]
                if curr_voice_id:
                    gridfs.GridFS(db, collection='voice').delete(ObjectId(curr_voice_id.grid_id))
            comment.update(**comment_serializer.validated_data)
            forum.save()
            return JsonResponse({"Message" : "Comment Updated"}, status=status.HTTP_201_CREATED, safe=False)
        return JsonResponse(comment_serializer.errors, safe=False, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def comment_report_api(request):
    comment_report = JSONParser().parse(request)
    req_auth_info = request.headers.get('Authorization')
    auth_info=base64.b64decode(req_auth_info[6:]).decode()
    auth_info=auth_info.split(":")
    req_user = User.objects.get(username=auth_info[0])
    comment_report["user_id"]=req_user.pk

    report_serializer = CommentReportSerializer(data=comment_report)
    if report_serializer.is_valid():
        report_serializer.save()
        return JsonResponse("Added Successfully",safe=False, status=status.HTTP_201_CREATED) 
    return JsonResponse(report_serializer.errors,safe=False, status=status.HTTP_400_BAD_REQUEST)
