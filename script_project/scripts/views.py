from django.shortcuts import render, get_object_or_404
from .models import Script, WordCloud, Scene, Character, Comment
from django.http import JsonResponse
import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
import time
import hashlib
import base64
import json
import requests
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

# 定义主页视图，渲染 index.html
def index(request):
    return render(request, 'index.html')  # 渲染index页面

def register_view(request):
    if request.method == 'POST':
        # 获取用户提交的表单数据
        user_id = request.POST['user_id']  # 用户账号
        password = request.POST['password']  # 密码
        username = request.POST['username']  # 昵称


        try:
            user = User.objects.create_user(username=user_id, password=password)  
            user.first_name = username  
            user.save()
            login(request, user)
            messages.success(request, "注册成功，已自动登录！")
            return redirect('index')  
        except Exception as e:
            messages.error(request, f"注册失败: {e}")
            return redirect('register')

    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        user_id = request.POST['user_id'] 
        password = request.POST['password']  

        # 通过 authenticate 验证用户
        user = authenticate(request, username=user_id, password=password)

        if user is not None:
            # 用户认证成功，执行登录操作
            login(request, user)
            messages.success(request, "登录成功！")
            return redirect('index')  # 跳转到主页
        else:
            # 用户认证失败，显示错误信息
            messages.error(request, "用户名或密码错误！")
            return redirect('login')

    return render(request, 'login.html')

# 用户登出视图
def logout_view(request):
    logout(request)
    return redirect('index')  # 登出后跳转到首页


# 定义剧本展示页面的视图，渲染 script.html
def script_view(request):
    title = request.GET.get('title')
    script = get_object_or_404(Script, scriptTitle=title)
    return render(request, 'script.html', {'scriptId': script.scriptId, 'title': title})


def get_wordcloud_data(request):
    title = request.GET.get('title')
    script = Script.objects.filter(scriptTitle=title).first()
    
    if script:
        wordcloud = WordCloud.objects.filter(scriptId=script).first()
        if wordcloud:
            return JsonResponse({'words': wordcloud.words})
        else:
            return JsonResponse({'error': '未找到该剧本的词云数据'}, status=404)
    else:
        return JsonResponse({'error': '未找到该剧本'}, status=404)
    
#时间轴  
def script_overview(request):
    title = request.GET.get('title')
    script = Script.objects.filter(scriptTitle=title).first()

    if script:
        scenes = Scene.objects.filter(scriptId=script).order_by('scene_id')
        # 计算每个时间轴项的 left 值
        for index, scene in enumerate(scenes):
            scene.left = index * 100  # 假设每个时间轴项的宽度为 100px
        return render(request, 'script.html', {'script': script, 'scenes': scenes})
    else:
        return render(request, 'script.html', {'error': '剧本未找到'})



def get_relationship_data(request):
    try:
        # 获取指定剧本的数据
        title = request.GET.get('title')
        if not title:
            return JsonResponse({'error': '缺少 title 参数'}, status=400)

        # 获取剧本实例
        script = Script.objects.filter(scriptTitle=title).first()
        if not script:
            return JsonResponse({'error': '剧本未找到'}, status=404)

        # 获取与剧本关联的所有角色
        characters = Character.objects.filter(script_id=script.scriptId)
        if not characters:
            return JsonResponse({'error': '角色未找到'}, status=404)

        # 获取角色关系数据（存储在 character_links 字段中）
        json_str = json.dumps(script.character_links)
        character_links = json.loads(json_str) if script.character_links else []

        # 构建节点数据
        nodes = []
        for char in characters:
            nodes.append({
                'id': char.character_id,
                'name': char.character_name,
                'symbolSize': char.symbol_size * 7,
                'value': char.value,
                'category': char.category,
                'image': char.image_url
            })

        # 构建链接数据（来自 character_links）
        links = [
            {
                'source': link['source'],
                'target': link['target']
            }
            for link in character_links
        ]

        # 获取所有唯一的角色类别
        categories = list(set(char.category for char in characters))

        # 返回节点和链接数据
        return JsonResponse({'nodes': nodes, 'links': links, 'categories': categories})

    except Script.DoesNotExist:
        return JsonResponse({'error': 'Script not found'}, status=404)
    

def show_comments(request):
    title = request.GET.get('title', None)
    sentiment = request.GET.get('sentiment', None)

    comments_query = Comment.objects.filter(script__scriptTitle=title)

    # 根据 sentiment 筛选评论
    if sentiment is not None:
        sentiment = int(sentiment)  # 确保 sentiment 是整数
        comments_query = comments_query.filter(sentiment=sentiment)

    comments = [
        {
            'username': comment.user_name,
            'comment_text': comment.comment_text,
            'comment_time': comment.comment_time,
            'sentiment': comment.sentiment  # 如果你有情感字段
        }
        for comment in comments_query
    ]

    return JsonResponse({'comments': comments})


def upload_comment(request):
    if request.method == 'POST':
        comment_text = request.POST.get('comment_text')
        title = request.GET.get('title')
        script = Script.objects.get(scriptTitle=title)
        if request.user.is_authenticated:
            username = request.user.first_name
        else:
            return JsonResponse({"message": "请先登录后再提交评论"}, status=400)
        app_id = 'f0efd843'  # 填写您的 App ID
        api_key = '60943baf87422b1a1f4addcd55074261'  # 填写您的 API Key
        sentiment = get_sentiment(comment_text, app_id, api_key)  # 获取情感分析结果

        sentiment_value = 0
        if sentiment == "褒义":
            sentiment_value = 1
        elif sentiment == "贬义":
            sentiment_value = -1
        
        new_comment = Comment(
            comment_text=comment_text,
            user_name=username,  # 使用 user_name 而不是 username
            script_id=script.scriptId,  # 确保正确的脚本外键
            comment_time=datetime.now(),
            sentiment=sentiment_value
        )

        new_comment.save()

        return JsonResponse({"message": "评论提交成功"}, status=200)
    
    return JsonResponse({"message": "请求方法错误"}, status=400)


def get_sentiment(text, app_id, api_key):
    url = "https://ltpapi.xfyun.cn/v2/sa"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "X-Appid": app_id,
        "X-CurTime": str(int(time.time())),
        "X-Param": base64.b64encode(json.dumps({"type": "dependent"}).encode('utf-8')).decode('utf-8'),
        "X-CheckSum": hashlib.md5((api_key + str(int(time.time())) + base64.b64encode(json.dumps({"type": "dependent"}).encode('utf-8')).decode('utf-8')).encode('utf-8')).hexdigest()
    }
    data = {"text": text}
    try:
        response = requests.post(url, headers=headers, data=data, timeout=10)
        result = response.json()
        if result['code'] == '0':
            sentiment = result['data']['sentiment']
            if sentiment == 0:
                return "中性"
            elif sentiment == 1:
                return "褒义"
            else:
                return "贬义"
        else:
            return "错误"
    except requests.exceptions.Timeout:
        return "请求超时"
    except requests.exceptions.RequestException as e:
        return f"请求失败: {str(e)}"

    
def get_sentiment_for_comments(script_id, app_id, api_key):
    # 获取剧本的所有评论
    comments = Comment.objects.filter(script_id=script_id)
    
    # 总评论数
    total_comments = len(comments)
    
    if total_comments == 0:
        return {"褒义": 0.0, "中性": 0.0, "贬义": 0.0}

    sentiment_counts = {
        "褒义": 0,
        "中性": 0,
        "贬义": 0
    }

    # 逐个评论进行情感分析
    for comment in comments:
        sentiment = get_sentiment(comment.comment_text, app_id, api_key)  # 调用情感分析API
        
        # 更新情感分析结果计数
        if sentiment in sentiment_counts:
            sentiment_counts[sentiment] += 1

    # 计算每种情感的比例
    sentiment_proportions = {
        "褒义": round(sentiment_counts["褒义"] / total_comments, 2),
        "中性": round(sentiment_counts["中性"] / total_comments, 2),
        "贬义": round(sentiment_counts["贬义"] / total_comments, 2)
    }

    return sentiment_proportions


def get_sentiment_stats(request):
    script_title = request.GET.get('title')
    
    try:
        script = Script.objects.get(scriptTitle=script_title)
    except Script.DoesNotExist:
        return JsonResponse({'error': '未找到该剧本'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'错误: {str(e)}'}, status=500)

    app_id = 'f0efd843'
    api_key = '60943baf87422b1a1f4addcd55074261'
    
    try:
        sentiment_proportions = get_sentiment_for_comments(script.scriptId, app_id, api_key)
        
        return JsonResponse({
            'sentiment_proportions': sentiment_proportions
        })
    
    except Exception as e:
        return JsonResponse({'error': f'获取情感分析失败: {str(e)}'}, status=500)


