from tortoise import fields

from app.schemas.menus import MenuType

from .base import BaseModel, TimestampMixin
from .enums import MethodType

class Api(BaseModel, TimestampMixin):
    path = fields.CharField(max_length=100, description="API路径", index=True)
    method = fields.CharEnumField(MethodType, description="请求方法", index=True)
    summary = fields.CharField(max_length=500, description="请求简介", index=True)
    tags = fields.CharField(max_length=100, description="API标签", index=True)

    class Meta:
        table = "api"


class Menu(BaseModel, TimestampMixin):
    name = fields.CharField(max_length=20, description="菜单名称", index=True)
    remark = fields.JSONField(null=True, description="保留字段", blank=True)
    menu_type = fields.CharEnumField(MenuType, null=True, blank=True, description="菜单类型")
    icon = fields.CharField(max_length=100, null=True, blank=True, description="菜单图标")
    path = fields.CharField(max_length=100, description="菜单路径", index=True)
    order = fields.IntField(default=0, description="排序", index=True)
    parent_id = fields.IntField(default=0, max_length=10, description="父菜单ID", index=True)
    is_hidden = fields.BooleanField(default=False, description="是否隐藏")
    component = fields.CharField(max_length=100, description="组件")
    keepalive = fields.BooleanField(default=True, description="存活")
    redirect = fields.CharField(max_length=100, null=True, blank=True, description="重定向")

    class Meta:
        table = "menu"

class Role(BaseModel, TimestampMixin):
    name = fields.CharField(max_length=20, unique=True, description="角色名称", index=True)
    desc = fields.CharField(max_length=500, null=True, blank=True, description="角色描述")
    menus = fields.ManyToManyField("models.Menu", related_name="role_menus")
    apis = fields.ManyToManyField("models.Api", related_name="role_apis")
    class Meta:
        table = "role"

class User(BaseModel, TimestampMixin):
    username = fields.CharField(max_length=20, unique=True, description="用户名称", index=True)
    alias = fields.CharField(max_length=30, null=True, description="姓名", index=True)
    email = fields.CharField(max_length=255, unique=True, description="邮箱", index=True)
    phone = fields.CharField(max_length=20, null=True, description="电话", index=True)
    password = fields.CharField(max_length=128, null=True, description="密码")
    is_active = fields.BooleanField(default=True, description="是否激活", index=True)
    is_superuser = fields.BooleanField(default=False, description="是否为超级管理员", index=True)
    last_login = fields.DatetimeField(null=True, description="最后登录时间", index=True)
    roles = fields.ManyToManyField("models.Role", related_name="user_roles")
    # dept_id = fields.IntField(null=True, description="部门ID", index=True)

    class Meta:
        table = "user"

    class PydanticMeta:
        # todo
        # computed = ["full_name"]
        ...

class AudioFiles(BaseModel):
    user = fields.ForeignKeyField("models.User", related_name="audio_files")
    file_name = fields.CharField(max_length=255)
    file_path = fields.CharField(max_length=255)
    text_info = fields.TextField()
    tone_name = fields.CharField(max_length=255,default=None,unique=True)
    tone_avatar = fields.CharField(max_length=255,default=None)
    cloned_voice = fields.BooleanField(default=False)
    build_in = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    deleted_at = fields.DatetimeField(null=True)
    tags = fields.ManyToManyField("models.Tags", related_name="audio_tags")

    class Meta:
        table = "audio_files"

class Tags(BaseModel):
    tag_name = fields.CharField(max_length=255, unique=True)
    
    class Meta:
        table = "tags"

class TTSOperations(BaseModel):
    user = fields.ForeignKeyField("models.User", related_name="tts_operations")
    input_text = fields.TextField()
    voice = fields.ForeignKeyField("models.AudioFiles", related_name="tts_operations_as_voice", null=True)
    output_audio_file = fields.ForeignKeyField("models.AudioFiles", related_name="tts_operations_as_output")
    created_at = fields.DatetimeField(auto_now_add=True)
    is_created = fields.BooleanField(default=False)

    class Meta:
        table = "tts_operations"

class History(BaseModel):
    user = fields.ForeignKeyField("models.User", related_name="history_user")
    tts = fields.ForeignKeyField("models.TTSOperations", related_name="history_tts")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "history"

class DeptClosure(BaseModel, TimestampMixin):
    ancestor = fields.IntField(description="父代", index=True)
    descendant = fields.IntField(description="子代", index=True)
    level = fields.IntField(default=0, description="深度", index=True)


class AuditLog(BaseModel, TimestampMixin):
    user_id = fields.IntField(description="用户ID", index=True)
    username = fields.CharField(max_length=64, default="", description="用户名称", index=True)
    module = fields.CharField(max_length=64, default="", description="功能模块", index=True)
    summary = fields.CharField(max_length=128, default="", description="请求描述", index=True)
    method = fields.CharField(max_length=10, default="", description="请求方法", index=True)
    path = fields.CharField(max_length=255, default="", description="请求路径", index=True)
    status = fields.IntField(default=-1, description="状态码", index=True)
    response_time = fields.IntField(default=0, description="响应时间(单位ms)", index=True)
