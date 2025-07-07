from django.db import models
from django.contrib.auth.models import User  
# Create your models here.
class Script(models.Model):
    scriptId = models.AutoField(primary_key=True)
    scriptTitle = models.CharField(max_length=255)
    script_id = models.CharField
    character_links = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return self.scriptTitle

# WordCloud 模型，用于存储词云数据
class WordCloud(models.Model):
    scriptId = models.ForeignKey(Script, on_delete=models.CASCADE, related_name='wordclouds')  # 外键，关联到 Script 表
    words = models.JSONField()  

    def __str__(self):
        return f"WordCloud for {self.scriptId.scriptTitle}"
    
# scene 模型，存储场景节点与文本
class Scene(models.Model):
    scriptId = models.ForeignKey('Script', on_delete=models.CASCADE) 
    scene_id = models.IntegerField()  
    scene_text = models.TextField()  

    class Meta:
        unique_together = ('scriptId', 'scene_id')  

# 人物模型，存放人物id，名字，图片url
class Character(models.Model):
    script = models.ForeignKey('Script', on_delete=models.CASCADE)  
    character_id = models.AutoField(primary_key=True)
    character_name = models.CharField(max_length=255)
    image_url = models.CharField(max_length=255, null=True, blank=True)  
    symbol_size = models.IntegerField(default=2)  
    value = models.IntegerField(default=0)  
    category = models.IntegerField(default=0) 

    def __str__(self):
        return f"角色名称: {self.character_name}, 角色ID: {self.character_id}, 图片: {self.image_url}"

class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)  # 自动生成 comment_id
    script = models.ForeignKey(Script, on_delete=models.CASCADE)  # 外键关系
    user_name = models.CharField(max_length=255, default='未知')
    comment_text = models.TextField()
    comment_time = models.DateTimeField()
    sentiment = models.IntegerField(default=0)

    def __str__(self):
        return f"评论 by {self.user_name} on {self.script.scriptTitle}"

